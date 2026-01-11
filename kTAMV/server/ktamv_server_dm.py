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
        Create blob detectors with parameters scaled for the current resolution.
        scale_factor: Area scale factor (linear_scale²). For 1280x720: scale_factor=4.0
        """
        area_scale = scale_factor

        # Standard Parameters
        self.standardParams = cv2.SimpleBlobDetector_Params()
        # Thresholds (not resolution dependent)
        self.standardParams.minThreshold = 1
        self.standardParams.maxThreshold = 50
        self.standardParams.thresholdStep = 1
        # Area (scale with resolution)
        self.standardParams.filterByArea = True
        self.standardParams.minArea = int(400 * area_scale)
        self.standardParams.maxArea = int(900 * area_scale)
        # Circularity (not resolution dependent)
        self.standardParams.filterByCircularity = True
        self.standardParams.minCircularity = 0.8
        self.standardParams.maxCircularity = 1
        # Convexity
        self.standardParams.filterByConvexity = True
        self.standardParams.minConvexity = 0.3
        self.standardParams.maxConvexity = 1
        # Inertia
        self.standardParams.filterByInertia = True
        self.standardParams.minInertiaRatio = 0.3

        # Relaxed Parameters
        self.relaxedParams = cv2.SimpleBlobDetector_Params()
        self.relaxedParams.minThreshold = 1
        self.relaxedParams.maxThreshold = 50
        self.relaxedParams.thresholdStep = 1
        self.relaxedParams.filterByArea = True
        self.relaxedParams.minArea = int(600 * area_scale)
        self.relaxedParams.maxArea = int(15000 * area_scale)
        self.relaxedParams.filterByCircularity = True
        self.relaxedParams.minCircularity = 0.6
        self.relaxedParams.maxCircularity = 1
        self.relaxedParams.filterByConvexity = True
        self.relaxedParams.minConvexity = 0.1
        self.relaxedParams.maxConvexity = 1
        self.relaxedParams.filterByInertia = True
        self.relaxedParams.minInertiaRatio = 0.3

        # Super Relaxed Parameters
        self.superRelaxedParams = cv2.SimpleBlobDetector_Params()
        self.superRelaxedParams.minThreshold = 20
        self.superRelaxedParams.maxThreshold = 200
        self.superRelaxedParams.filterByArea = True
        self.superRelaxedParams.minArea = int(200 * area_scale)
        self.superRelaxedParams.filterByCircularity = True
        self.superRelaxedParams.minCircularity = 0.5
        self.superRelaxedParams.filterByConvexity = True
        self.superRelaxedParams.minConvexity = 0.5
        self.superRelaxedParams.filterByInertia = True
        self.superRelaxedParams.minInertiaRatio = 0.5
        self.superRelaxedParams.filterByColor = False
        self.superRelaxedParams.minDistBetweenBlobs = 2

        # Create 3 detectors
        self.detector = cv2.SimpleBlobDetector_create(self.standardParams)
        self.relaxedDetector = cv2.SimpleBlobDetector_create(self.relaxedParams)
        self.superRelaxedDetector = cv2.SimpleBlobDetector_create(self.superRelaxedParams)

        self.log("Detectors created with area_scale=%.2f (minArea: %d-%d)" %
                 (area_scale, self.standardParams.minArea, self.relaxedParams.maxArea))

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

        # return value for keypoints
        keypoints = None
        center = (None, None)
        keypointColor = (0,0,255)

        # Preprocess images with all algorithms including CLAHE
        preprocessorImage0 = self.preprocessImage(frameInput=nozzleDetectFrame, algorithm=0)
        preprocessorImage1 = self.preprocessImage(frameInput=nozzleDetectFrame, algorithm=1)
        preprocessorImage2 = self.preprocessImage(frameInput=nozzleDetectFrame, algorithm=2)
        preprocessorImage3 = self.preprocessImage(frameInput=nozzleDetectFrame, algorithm=3)  # CLAHE
        preprocessorImage4 = self.preprocessImage(frameInput=nozzleDetectFrame, algorithm=4)  # CLAHE + morphology

        # Detection cascade - try progressively more relaxed detection
        detection_combos = [
            (self.detector, preprocessorImage0, (0,0,255), "standard+YUV"),
            (self.detector, preprocessorImage1, (0,255,0), "standard+triangle"),
            (self.detector, preprocessorImage3, (0,255,255), "standard+CLAHE"),
            (self.relaxedDetector, preprocessorImage0, (255,0,0), "relaxed+YUV"),
            (self.relaxedDetector, preprocessorImage1, (39,127,255), "relaxed+triangle"),
            (self.relaxedDetector, preprocessorImage3, (255,127,39), "relaxed+CLAHE"),
            (self.relaxedDetector, preprocessorImage4, (127,255,127), "relaxed+CLAHE+morph"),
            (self.superRelaxedDetector, preprocessorImage2, (39,255,127), "superRelaxed+median"),
            (self.superRelaxedDetector, preprocessorImage4, (255,0,255), "superRelaxed+CLAHE+morph"),
        ]

        for i, (detector, preprocessed, color, name) in enumerate(detection_combos):
            keypoints = detector.detect(preprocessed)

            if len(keypoints) == 1:
                # Perfect: exactly one detection
                keypointColor = color
                self.__algorithm = i + 1
                self.log("Nozzle detected with algo %d (%s)" % (self.__algorithm, name))
                break
            elif len(keypoints) > 1:
                # Multiple detections: pick the most centered one
                best_idx = self.find_closest_keypoint(keypoints, nozzleDetectFrame.shape)
                if best_idx is not None:
                    # Keep only the best keypoint
                    keypoints = [keypoints[best_idx]]
                    keypointColor = color
                    self.__algorithm = i + 1
                    self.log("Nozzle: picked best of %d with algo %d (%s)" % (len(keypoints)+1, self.__algorithm, name))
                    break

        # If blob detection failed, try HoughCircles as fallback
        if keypoints is None or len(keypoints) == 0:
            self.log("Blob detection failed, trying HoughCircles...")
            hough_result = self.detectWithHoughCircles(nozzleDetectFrame, preprocessorImage3)
            if hough_result is not None:
                keypoints = hough_result
                keypointColor = (255, 165, 0)  # Orange for HoughCircles
                self.__algorithm = 100  # Special code for HoughCircles
                self.log("Nozzle detected with HoughCircles")

        if keypoints is None or len(keypoints) == 0:
            self.log("Nozzle detection failed completely.")
            
            
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

    def adjust_gamma(self, image, gamma=1.2):
        # build a lookup table mapping the pixel values [0, 255] to
        # their adjusted gamma values
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype( 'uint8' )
        # apply gamma correction using the lookup table
        return cv2.LUT(image, table)

