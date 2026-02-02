import copy, time, cv2, numpy as np
from ktamv_server_io import Ktamv_Server_Io as io


class Ktamv_Server_Detection_Manager:
    uv = [None, None]
    __algorithm = None
    __io = None

    ##### Setup functions
    # init function
    def __init__(self, log, camera_url, cloud_url, send_to_cloud = False, *args, **kwargs):
        try:
            self.log = log

            # send calling to log
            self.log('*** calling DetectionManager.__init__')

            # Whether to send the images to the cloud after detection.
            self.send_to_cloud = send_to_cloud

            # The already initialized io object.
            self.__io = io(log=log, camera_url=camera_url, cloud_url=cloud_url, save_image=False)

            # This is the last successful algorithm used by the nozzle detection. Should be reset at tool change. Will have to change.
            self.__algorithm = None

            # TAMV has 2 detectors, one for standard and one for relaxed
            self.createDetectors()

            # Create CLAHE for adaptive contrast enhancement
            self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

            # HoughCircles parameters (can be tuned per setup)
            self.hough_dp = 1.2
            self.hough_minDist = 50
            self.hough_param1 = 50
            self.hough_param2 = 30
            self.hough_minRadius = 10
            self.hough_maxRadius = 50

            # send exiting to log
            self.log('*** exiting DetectionManager.__init__')
        except Exception as e:
            self.log('*** exception in DetectionManager.__init__: %s' % str(e))
            raise e

    # timeout = 20: If no nozzle found in this time, timeout the function
    # min_matches = 3: Minimum amount of matches to confirm toolhead position after a move
    # xy_tolerance = 1: If the nozzle position is within this tolerance, it's considered a match. 1.0 would be 1 pixel. Only whole numbers are supported.
    # put_frame_func: Function to put the frame into the main program
    def recursively_find_nozzle_position(self, put_frame_func, min_matches, timeout, xy_tolerance):
        self.log('*** calling recursively_find_nozzle_position')
        start_time = time.time()  # Get the current time
        last_pos = (0,0)
        pos_matches = 0
        pos = None

        while time.time() - start_time < timeout:
            frame = self.__io.get_single_frame()
            positions, processed_frame = self.nozzleDetection(frame)
            if processed_frame is not None:
                put_frame_func(processed_frame)

            self.log('recursively_find_nozzle_position positions: %s' % str(positions))

            if positions is None or len(positions) == 0:
                continue

            pos = positions
            # Only compare XY position, not radius...
            if abs(pos[0] - last_pos[0]) <= xy_tolerance and abs(pos[1] - last_pos[1]) <= xy_tolerance:
                pos_matches += 1
                if pos_matches >= min_matches:
                    self.log("recursively_find_nozzle_position found %i matches and returning" % pos_matches)
                    # Send the frame and detection to the cloud if enabled.
                    if self.send_to_cloud:
                        self.__io.send_frame_to_cloud(frame, pos, self.__algorithm)
                    break
            else:
                self.log("Position found does not match last position. Last position: %s, current position: %s" % (str(last_pos), str(pos)))   
                self.log("Difference: X%.3f Y%.3f" % (abs(pos[0] - last_pos[0]), abs(pos[1] - last_pos[1])))
                pos_matches = 0

            last_pos = pos
            # Wait 0.3 to leave time for the webcam server to catch up
            # Crowsnest usually caches 0.3 seconds of frames
            time.sleep(0.3)

        self.log("recursively_find_nozzle_position found: %s" % str(last_pos))
        self.log('*** exiting recursively_find_nozzle_position')
        return pos

    def get_preview_frame(self, put_frame_func):
        # self.log('*** calling get_preview_frame')

        frame = self.__io.get_single_frame()
        _, processed_frame = self.nozzleDetection(frame)
        if processed_frame is not None:
            put_frame_func(processed_frame)

        # self.log('*** exiting get_preview_frame')
        return

# ----------------- TAMV Nozzle Detection as tested in ktamv_cv -----------------

    # Base resolution for parameter scaling (original kTAMV values)
    BASE_WIDTH = 640
    BASE_HEIGHT = 480

    def createDetectors(self, scale_factor=1.0):
        """
        Create blob detectors for DARK nozzle openings.
        The nozzle opening is DARK - we need blobColor=0!
        """
        area_scale = scale_factor

        # Dark blob detector - specifically for dark nozzle openings
        self.standardParams = cv2.SimpleBlobDetector_Params()
        self.standardParams.minThreshold = 10
        self.standardParams.maxThreshold = 200
        self.standardParams.thresholdStep = 10
        self.standardParams.filterByArea = True
        self.standardParams.minArea = int(200 * area_scale)
        self.standardParams.maxArea = int(50000 * area_scale)
        self.standardParams.filterByCircularity = True
        self.standardParams.minCircularity = 0.5
        self.standardParams.filterByConvexity = False
        self.standardParams.filterByInertia = False
        self.standardParams.filterByColor = True
        self.standardParams.blobColor = 0  # DARK blobs only!

        # Relaxed dark blob detector
        self.relaxedParams = cv2.SimpleBlobDetector_Params()
        self.relaxedParams.minThreshold = 5
        self.relaxedParams.maxThreshold = 200
        self.relaxedParams.thresholdStep = 10
        self.relaxedParams.filterByArea = True
        self.relaxedParams.minArea = int(100 * area_scale)
        self.relaxedParams.maxArea = int(80000 * area_scale)
        self.relaxedParams.filterByCircularity = False
        self.relaxedParams.filterByConvexity = False
        self.relaxedParams.filterByInertia = False
        self.relaxedParams.filterByColor = True
        self.relaxedParams.blobColor = 0  # DARK blobs only!

        # Super relaxed - any dark blob
        self.superRelaxedParams = cv2.SimpleBlobDetector_Params()
        self.superRelaxedParams.minThreshold = 1
        self.superRelaxedParams.maxThreshold = 255
        self.superRelaxedParams.thresholdStep = 20
        self.superRelaxedParams.filterByArea = True
        self.superRelaxedParams.minArea = int(50 * area_scale)
        self.superRelaxedParams.filterByCircularity = False
        self.superRelaxedParams.filterByConvexity = False
        self.superRelaxedParams.filterByInertia = False
        self.superRelaxedParams.filterByColor = True
        self.superRelaxedParams.blobColor = 0  # DARK blobs only!

        # Create detectors
        self.detector = cv2.SimpleBlobDetector_create(self.standardParams)
        self.relaxedDetector = cv2.SimpleBlobDetector_create(self.relaxedParams)
        self.superRelaxedDetector = cv2.SimpleBlobDetector_create(self.superRelaxedParams)

        self.log("Dark-blob detectors created (blobColor=0, minArea: %d, scale: %.2f)" %
                 (self.standardParams.minArea, area_scale))

    def updateDetectorsForImage(self, image):
        """
        Recalculate detectors if image resolution changed.
        """
        h, w = image.shape[:2]
        linear_scale = (w / self.BASE_WIDTH + h / self.BASE_HEIGHT) / 2.0
        area_scale = linear_scale ** 2

        # Also scale HoughCircles parameters
        self.hough_minRadius = int(10 * linear_scale)
        self.hough_maxRadius = int(50 * linear_scale)

        # Only recreate if scale changed significantly
        if not hasattr(self, '_current_scale') or abs(self._current_scale - area_scale) > 0.1:
            self._current_scale = area_scale
            self.createDetectors(area_scale)
            self.log("Resolution %dx%d detected, scale_factor=%.2f" % (w, h, area_scale))

    def nozzleDetection(self, image):
        # working frame object
        nozzleDetectFrame = copy.deepcopy(image)

        # Auto-scale detection parameters for current image resolution
        self.updateDetectorsForImage(nozzleDetectFrame)

        # Get image dimensions for center region filtering
        h, w = nozzleDetectFrame.shape[:2]
        img_center_x, img_center_y = w // 2, h // 2

        # Define center region of interest (ROI) - only consider detections within this area
        # ROI is 60% of image width/height around center (larger for tool offsets)
        roi_margin_x = int(w * 0.30)  # 30% margin on each side = 60% ROI
        roi_margin_y = int(h * 0.30)
        roi_x_min = img_center_x - roi_margin_x
        roi_x_max = img_center_x + roi_margin_x
        roi_y_min = img_center_y - roi_margin_y
        roi_y_max = img_center_y + roi_margin_y

        # return value for keypoints
        keypoints = None
        center = (None, None)
        keypointColor = (0,0,255)

        # PRIMARY: Find darkest circular region (the nozzle opening is the darkest spot!)
        keypoints = self.findNozzleByDarkCenter(nozzleDetectFrame, (img_center_x, img_center_y), search_radius=200)
        if keypoints is not None and len(keypoints) > 0:
            keypointColor = (0, 255, 0)  # Green
            self.__algorithm = 1
        else:
            self.log("DarkCenter failed, no nozzle detected")
            
            
        # Get image dimensions for dynamic center calculation
        h, w = nozzleDetectFrame.shape[:2]
        center_x, center_y = w // 2, h // 2

        # process keypoint
        if keypoints is not None and len(keypoints) >= 1:
            # If multiple keypoints are found, use the one closest to the center
            if len(keypoints) > 1:
                closest_index = self.find_closest_keypoint(keypoints, nozzleDetectFrame.shape)
                best_keypoint = keypoints[closest_index]
            else:
                best_keypoint = keypoints[0]

            # Create center from best keypoint
            (x, y) = np.around(best_keypoint.pt)
            x, y = int(x), int(y)
            center = (x, y)

            # Create radius from keypoint size
            keypointRadius = int(np.around(best_keypoint.size / 2))

            # Draw filled circle overlay
            circleFrame = cv2.circle(img=nozzleDetectFrame, center=center, radius=keypointRadius, color=keypointColor, thickness=-1, lineType=cv2.LINE_AA)
            nozzleDetectFrame = cv2.addWeighted(circleFrame, 0.4, nozzleDetectFrame, 0.6, 0)
            nozzleDetectFrame = cv2.circle(img=nozzleDetectFrame, center=center, radius=keypointRadius, color=(0,0,0), thickness=1, lineType=cv2.LINE_AA)

            # Draw crosshair at detected center
            nozzleDetectFrame = cv2.line(nozzleDetectFrame, (x-5, y), (x+5, y), (255,255,255), 2)
            nozzleDetectFrame = cv2.line(nozzleDetectFrame, (x, y-5), (x, y+5), (255,255,255), 2)
        else:
            # No keypoints found, draw indicator circle at image center
            keypointRadius = 17
            nozzleDetectFrame = cv2.circle(img=nozzleDetectFrame, center=(center_x, center_y), radius=keypointRadius, color=(0,0,0), thickness=3, lineType=cv2.LINE_AA)
            nozzleDetectFrame = cv2.circle(img=nozzleDetectFrame, center=(center_x, center_y), radius=keypointRadius+1, color=(0,0,255), thickness=1, lineType=cv2.LINE_AA)
            center = None

        # Draw ROI rectangle to show detection area
        cv2.rectangle(nozzleDetectFrame, (roi_x_min, roi_y_min), (roi_x_max, roi_y_max), (100, 100, 100), 1)

        # Draw crosshair at image center (dynamic based on actual resolution)
        nozzleDetectFrame = cv2.line(nozzleDetectFrame, (center_x, 0), (center_x, h), (0,0,0), 2)
        nozzleDetectFrame = cv2.line(nozzleDetectFrame, (0, center_y), (w, center_y), (0,0,0), 2)
        nozzleDetectFrame = cv2.line(nozzleDetectFrame, (center_x, 0), (center_x, h), (255,255,255), 1)
        nozzleDetectFrame = cv2.line(nozzleDetectFrame, (0, center_y), (w, center_y), (255,255,255), 1)

        # return(center, nozzleDetectFrame)
        return(center, nozzleDetectFrame)

    # Image detection preprocessors
    def preprocessImage(self, frameInput, algorithm=0):
        try:
            outputFrame = self.adjust_gamma(image=frameInput, gamma=1.2)
            height, width, channels = outputFrame.shape
        except:
            outputFrame = copy.deepcopy(frameInput)

        if algorithm == 0:
            # Original: YUV + adaptive threshold
            yuv = cv2.cvtColor(outputFrame, cv2.COLOR_BGR2YUV)
            yuvPlanes = cv2.split(yuv)
            yuvPlanes_0 = cv2.GaussianBlur(yuvPlanes[0], (7,7), 6)
            yuvPlanes_0 = cv2.adaptiveThreshold(yuvPlanes_0, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 1)
            outputFrame = cv2.cvtColor(yuvPlanes_0, cv2.COLOR_GRAY2BGR)

        elif algorithm == 1:
            # Original: grayscale + triangle threshold
            outputFrame = cv2.cvtColor(outputFrame, cv2.COLOR_BGR2GRAY)
            thr_val, outputFrame = cv2.threshold(outputFrame, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_TRIANGLE)
            outputFrame = cv2.GaussianBlur(outputFrame, (7,7), 6)
            outputFrame = cv2.cvtColor(outputFrame, cv2.COLOR_GRAY2BGR)

        elif algorithm == 2:
            # Original: median blur (for superRelaxed)
            gray = cv2.cvtColor(frameInput, cv2.COLOR_BGR2GRAY)
            outputFrame = cv2.medianBlur(gray, 5)
            outputFrame = cv2.cvtColor(outputFrame, cv2.COLOR_GRAY2BGR)

        elif algorithm == 3:
            # NEW: CLAHE (Contrast Limited Adaptive Histogram Equalization)
            # Much better for varying lighting conditions
            gray = cv2.cvtColor(outputFrame, cv2.COLOR_BGR2GRAY)
            enhanced = self.clahe.apply(gray)
            # Bilateral filter preserves edges while reducing noise
            filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
            # Adaptive threshold for robust binarization
            binary = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
            outputFrame = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

        elif algorithm == 4:
            # NEW: CLAHE + morphological operations
            # Best for cleaning up reflections and noise
            gray = cv2.cvtColor(outputFrame, cv2.COLOR_BGR2GRAY)
            enhanced = self.clahe.apply(gray)
            # Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(enhanced, (5,5), 0)
            # Otsu threshold for automatic threshold selection
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Morphological operations to clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            # Opening removes small noise
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            # Closing fills small holes
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
            outputFrame = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)

        return outputFrame

    def findNozzleByDarkCenter(self, image, image_center, search_radius=200):
        """
        Find nozzle using HoughCircles to detect the circular nozzle opening.
        This finds the CENTER of the circle, not just the darkest pixel.
        """
        try:
            h, w = image.shape[:2]
            cx, cy = image_center

            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()

            # Define search region around center
            x1 = max(0, cx - search_radius)
            x2 = min(w, cx + search_radius)
            y1 = max(0, cy - search_radius)
            y2 = min(h, cy + search_radius)

            roi = gray[y1:y2, x1:x2]

            # Blur and enhance contrast for HoughCircles
            blurred = cv2.GaussianBlur(roi, (5, 5), 0)

            # Enhance contrast with CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(blurred)

            # Use HoughCircles to find circular openings
            # The nozzle opening is a CIRCLE - find it by shape, not just darkness
            circles = cv2.HoughCircles(
                enhanced,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=20,
                param1=100,
                param2=15,  # Very low = detect more circles
                minRadius=5,
                maxRadius=100
            )

            nozzle_x, nozzle_y, radius = None, None, 15

            if circles is not None:
                circles = np.uint16(np.around(circles))
                roi_cx, roi_cy = roi.shape[1] // 2, roi.shape[0] // 2

                # Find the circle closest to ROI center that is also DARK inside
                best_circle = None
                best_score = float('inf')

                for circle in circles[0, :]:
                    circ_x, circ_y, circ_r = circle

                    # Check if circle center is dark (it should be the nozzle opening)
                    inner_brightness = blurred[max(0,circ_y-3):circ_y+3, max(0,circ_x-3):circ_x+3].mean()

                    # Score: prefer dark AND close to center
                    dist_to_center = np.sqrt((circ_x - roi_cx)**2 + (circ_y - roi_cy)**2)
                    score = dist_to_center + inner_brightness * 0.5

                    if score < best_score:
                        best_score = score
                        best_circle = circle

                if best_circle is not None:
                    nozzle_x = x1 + best_circle[0]
                    nozzle_y = y1 + best_circle[1]
                    radius = best_circle[2]

            # Fallback to darkest point if no circles found
            if nozzle_x is None:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(blurred)
                nozzle_x = x1 + min_loc[0]
                nozzle_y = y1 + min_loc[1]
                radius = 15

            class FakeKeypoint:
                def __init__(self, x, y, size):
                    self.pt = (float(x), float(y))
                    self.size = float(size)

            self.log("DarkCenter: nozzle at (%d, %d), min_val=%d, radius=%.1f" % (nozzle_x, nozzle_y, min_val, radius))
            return [FakeKeypoint(nozzle_x, nozzle_y, max(radius * 2, 20))]

        except Exception as e:
            self.log("findNozzleByDarkCenter error: %s" % str(e))

        return None

    def _get_region_brightness(self, gray_image, cx, cy, radius):
        """Get average brightness in a circular region."""
        h, w = gray_image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (cx, cy), radius, 255, -1)
        return cv2.mean(gray_image, mask=mask)[0]

    def _get_ring_brightness(self, gray_image, cx, cy, inner_radius, outer_radius):
        """Get average brightness in a ring (annulus) region."""
        h, w = gray_image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (cx, cy), outer_radius, 255, -1)
        cv2.circle(mask, (cx, cy), inner_radius, 0, -1)
        mean_val = cv2.mean(gray_image, mask=mask)[0]
        return mean_val if mean_val > 0 else 0

    def detectWithHoughCircles(self, original_frame, preprocessed_frame):
        """
        HoughCircles fallback detection when blob detection fails.
        Returns a list with a single keypoint-like object if successful.
        """
        try:
            # Convert to grayscale if needed
            if len(preprocessed_frame.shape) == 3:
                gray = cv2.cvtColor(preprocessed_frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = preprocessed_frame

            # Apply additional blur for HoughCircles
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)

            # Detect circles using HoughCircles
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=self.hough_dp,
                minDist=self.hough_minDist,
                param1=self.hough_param1,
                param2=self.hough_param2,
                minRadius=self.hough_minRadius,
                maxRadius=self.hough_maxRadius
            )

            if circles is not None:
                circles = np.uint16(np.around(circles))
                # Get image center
                h, w = original_frame.shape[:2]
                center_x, center_y = w // 2, h // 2

                # Find circle closest to image center
                best_circle = None
                min_dist = float('inf')

                for circle in circles[0, :]:
                    x, y, r = circle
                    dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if dist < min_dist:
                        min_dist = dist
                        best_circle = (x, y, r)

                if best_circle is not None:
                    # Create a keypoint-like object
                    class FakeKeypoint:
                        def __init__(self, x, y, size):
                            self.pt = (float(x), float(y))
                            self.size = float(size * 2)  # diameter

                    return [FakeKeypoint(best_circle[0], best_circle[1], best_circle[2])]

        except Exception as e:
            self.log("HoughCircles error: %s" % str(e))

        return None

    def findDarkestCircularRegion(self, image, roi_center, roi_radius=100):
        """
        Find the center of the darkest circular region near the image center.
        This specifically targets the nozzle opening (dark hole).
        Filters by expected nozzle size (0.4-1.0mm at ~0.009mm/px = 20-60px radius)
        Returns a keypoint-like object or None.
        """
        try:
            h, w = image.shape[:2]
            cx, cy = roi_center

            # Expected nozzle radius range in pixels (at ~0.009mm/px for 1280x720)
            # 0.4mm nozzle = ~22px radius, 1.0mm nozzle = ~55px radius
            # Scale based on image resolution
            scale = (w / 640 + h / 480) / 2.0
            min_nozzle_radius = int(15 * scale)  # ~0.3mm minimum
            max_nozzle_radius = int(70 * scale)  # ~1.2mm maximum

            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()

            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Create ROI mask around center
            roi_x1 = max(0, cx - roi_radius)
            roi_x2 = min(w, cx + roi_radius)
            roi_y1 = max(0, cy - roi_radius)
            roi_y2 = min(h, cy + roi_radius)

            roi = blurred[roi_y1:roi_y2, roi_x1:roi_x2]

            # Find the minimum (darkest) point in the ROI
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(roi)

            # Refine by finding the centroid of the dark region
            # Threshold to find pixels near the minimum value
            threshold = min_val + 40  # Allow some tolerance
            _, binary = cv2.threshold(roi, threshold, 255, cv2.THRESH_BINARY_INV)

            # Find contours of the dark region
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Find the best contour: closest to darkest point AND within nozzle size range
                best_contour = None
                best_score = float('inf')

                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area < 100:  # Skip tiny noise
                        continue

                    # Calculate equivalent radius
                    radius = np.sqrt(area / np.pi)

                    # Skip if outside nozzle size range
                    if radius < min_nozzle_radius or radius > max_nozzle_radius:
                        continue

                    M = cv2.moments(contour)
                    if M["m00"] > 0:
                        cont_cx = int(M["m10"] / M["m00"])
                        cont_cy = int(M["m01"] / M["m00"])
                        dist = np.sqrt((cont_cx - min_loc[0])**2 + (cont_cy - min_loc[1])**2)

                        # Score: prefer close to darkest point AND good size
                        # Ideal size is around 0.4-0.6mm nozzle (30-45px radius)
                        ideal_radius = 35 * scale
                        size_penalty = abs(radius - ideal_radius) * 0.5
                        score = dist + size_penalty

                        if score < best_score:
                            best_score = score
                            best_contour = contour

                if best_contour is not None:
                    # Get the centroid of the best contour
                    M = cv2.moments(best_contour)
                    if M["m00"] > 0:
                        dark_x = roi_x1 + int(M["m10"] / M["m00"])
                        dark_y = roi_y1 + int(M["m01"] / M["m00"])

                        # Calculate equivalent radius
                        area = cv2.contourArea(best_contour)
                        radius = np.sqrt(area / np.pi)

                        class FakeKeypoint:
                            def __init__(self, x, y, size):
                                self.pt = (float(x), float(y))
                                self.size = float(size)

                        return [FakeKeypoint(dark_x, dark_y, radius * 2)]

        except Exception as e:
            self.log("findDarkestCircularRegion error: %s" % str(e))

        return None

    def find_closest_keypoint(self, keypoints, image_shape=None):
        """
        Find the keypoint closest to the image center.
        Handles variable image sizes instead of hardcoded 320x240.
        """
        closest_index = None
        closest_distance = float('inf')

        # Use image center if shape provided, otherwise default to 640x480
        if image_shape is not None:
            h, w = image_shape[:2]
            target_point = np.array([w // 2, h // 2])
        else:
            target_point = np.array([320, 240])

        for i, keypoint in enumerate(keypoints):
            point = np.array(keypoint.pt)
            distance = np.linalg.norm(point - target_point)

            if distance < closest_distance:
                closest_distance = distance
                closest_index = i

        return closest_index

    def validate_nozzle_contrast(self, image, keypoint, min_contrast=30):
        """
        Validate that a detected blob has the contrast pattern of a nozzle opening.
        A nozzle should have a dark center (the opening) surrounded by brighter material.
        Returns True if the contrast pattern matches a nozzle.
        """
        try:
            x, y = int(keypoint.pt[0]), int(keypoint.pt[1])
            radius = max(int(keypoint.size / 2), 5)
            h, w = image.shape[:2]

            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Ensure we're within image bounds
            inner_r = max(radius // 3, 3)
            outer_r = min(radius * 2, 50)

            x_min = max(0, x - outer_r)
            x_max = min(w, x + outer_r)
            y_min = max(0, y - outer_r)
            y_max = min(h, y + outer_r)

            if x_max - x_min < 10 or y_max - y_min < 10:
                return True  # Too small to validate, accept it

            # Sample inner region (should be darker - the nozzle opening)
            inner_mask = np.zeros((y_max - y_min, x_max - x_min), dtype=np.uint8)
            cv2.circle(inner_mask, (x - x_min, y - y_min), inner_r, 255, -1)
            inner_region = gray[y_min:y_max, x_min:x_max]
            inner_mean = cv2.mean(inner_region, mask=inner_mask)[0]

            # Sample outer ring (should be brighter - the nozzle tip)
            outer_mask = np.zeros((y_max - y_min, x_max - x_min), dtype=np.uint8)
            cv2.circle(outer_mask, (x - x_min, y - y_min), outer_r, 255, -1)
            cv2.circle(outer_mask, (x - x_min, y - y_min), radius, 0, -1)  # Remove inner
            outer_mean = cv2.mean(inner_region, mask=outer_mask)[0]

            # Nozzle opening should be darker than surrounding
            contrast = outer_mean - inner_mean

            # Removed verbose logging for performance
            return contrast >= min_contrast

        except Exception as e:
            self.log("Contrast validation error: %s" % str(e))
            return True  # On error, accept the detection

    def filter_keypoints_by_contrast(self, image, keypoints, min_contrast=20):
        """
        Filter keypoints to only those with valid nozzle contrast pattern.
        """
        if keypoints is None or len(keypoints) == 0:
            return keypoints

        valid_keypoints = []
        for kp in keypoints:
            if self.validate_nozzle_contrast(image, kp, min_contrast):
                valid_keypoints.append(kp)

        if len(valid_keypoints) == 0:
            self.log("All keypoints failed contrast check, using original")
            return keypoints  # Fall back to original if all fail

        return valid_keypoints

    def adjust_gamma(self, image, gamma=1.2):
        # build a lookup table mapping the pixel values [0, 255] to
        # their adjusted gamma values
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype( 'uint8' )
        # apply gamma correction using the lookup table
        return cv2.LUT(image, table)

