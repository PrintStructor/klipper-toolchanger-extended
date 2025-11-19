# Contributing to Klipper Toolchanger Extended

Thank you for your interest in contributing to Klipper Toolchanger Extended! This document provides guidelines and instructions for contributing to the project.

---

## 🎯 Ways to Contribute

There are many ways to contribute to this project:

- **Report bugs** - Help us identify and fix issues
- **Suggest features** - Share ideas for improvements
- **Improve documentation** - Fix typos, add examples, clarify instructions
- **Submit code** - Fix bugs or implement new features
- **Test changes** - Help validate new features on real hardware
- **Share configurations** - Contribute working setups for different printers

---

## 🐛 Reporting Bugs

### Before Submitting a Bug Report

1. **Check existing issues** - Your issue might already be reported
2. **Update to latest version** - The bug might already be fixed
3. **Test with example configuration** - Rule out configuration issues
4. **Check Klipper logs** - Look for error messages

### Submitting a Good Bug Report

Use the **Bug Report** template and include:

**Required Information:**
- Klipper Toolchanger Extended version (git commit hash)
- Klipper version
- Hardware configuration (printer, toolheads, probes)
- Steps to reproduce the issue
- Expected vs actual behavior
- Relevant log excerpts

**Helpful Additions:**
- Configuration files (sanitize any sensitive data)
- Photos/videos of the issue
- Console output
- Minimal test case that reproduces the issue

**Example:**
```markdown
## Bug Description
Tool detection fails during pickup on T2 only

## Environment
- Klipper Toolchanger Extended: v1.0.0 (commit abc123)
- Klipper: v0.12.0
- Hardware: VORON 2.4, 6-tool ATOM setup
- Probe: Beacon RevH

## Steps to Reproduce
1. Home all axes
2. SET_INITIAL_TOOL TOOL=0
3. T2  # Try to switch to T2
4. Tool pickup fails at verification stage

## Expected Behavior
T2 should be picked up successfully

## Actual Behavior
Error: "Tool not detected at verification point"
Detection pin reads: open (should be triggered)

## Logs
[toolchanger.py] Stage 1 pickup started
[toolchanger.py] Verification point reached
[tool.py] T2 detect_state: 0 (ABSENT)
[toolchanger.py] ERROR: Tool detection failed

## Additional Context
- T0, T1, T3-T5 work correctly
- QUERY_FILAMENT_SENSOR shows T2 sensor working in isolation
- Mechanical alignment verified
```

---

## 💡 Suggesting Features

### Before Suggesting a Feature

1. **Check existing feature requests** - It might already be planned
2. **Check the roadmap** - See if it aligns with project direction
3. **Consider if it's generally useful** - Will others benefit?

### Submitting a Good Feature Request

Use the **Feature Request** template and include:

- **Problem statement** - What problem does this solve?
- **Proposed solution** - How should it work?
- **Alternatives considered** - What other approaches exist?
- **Additional context** - Examples, mockups, references

**Example:**
```markdown
## Feature Description
Add automatic dock position learning

## Problem Statement
Manual dock position configuration is time-consuming and error-prone.
Users must manually jog to each position and record coordinates.

## Proposed Solution
Add a macro `LEARN_DOCK_POSITIONS` that:
1. Prompts user to manually position toolhead at each dock
2. Records coordinates when user confirms position
3. Automatically updates tool configs with learned positions
4. Provides before/after comparison

## Benefits
- Faster initial setup
- Reduces configuration errors
- Easier for new users

## Implementation Ideas
- Use `QUERY_PROBE` to help with alignment
- Store temp values during learning
- Only update config after user confirmation
- Include backup of previous values

## Alternatives Considered
- GUI-based web interface for positioning
- Camera-based auto-detection (too complex)
- Keep manual process (current state)
```

---

## 📝 Improving Documentation

Documentation improvements are always welcome!

### Areas for Improvement

- Fix typos and grammatical errors
- Add missing explanations
- Improve examples
- Add troubleshooting tips
- Translate documentation
- Add diagrams or photos

### Documentation Guidelines

- Use clear, simple language
- Include code examples where helpful
- Test all commands before documenting
- Follow existing formatting style
- Update table of contents if needed

### How to Submit Documentation Changes

1. Fork the repository
2. Make your changes
3. Test that formatting renders correctly
4. Submit a pull request with description of changes

---

## 💻 Contributing Code

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/klipper-toolchanger-extended.git
cd klipper-toolchanger-extended

# Add upstream remote
git remote add upstream https://github.com/PrintStructor/klipper-toolchanger-extended.git

# Create a feature branch
git checkout -b feature/your-feature-name
```

### Code Standards

#### Python Code
- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable names
- Add docstrings to classes and functions
- Keep functions focused and concise
- Handle errors gracefully
- Avoid breaking changes to public APIs

**Example:**
```python
class ToolManager:
    """Manages tool state and detection.
    
    This class handles tool detection, state management, and
    provides methods for safe tool changes.
    """
    
    def verify_tool_present(self, tool_number):
        """Verify if specified tool is currently detected.
        
        Args:
            tool_number (int): Tool number to check (0-5)
            
        Returns:
            bool: True if tool is detected, False otherwise
            
        Raises:
            ValueError: If tool_number is out of range
        """
        if not 0 <= tool_number < self.max_tools:
            raise ValueError(f"Tool number {tool_number} out of range")
        
        # Implementation...
```

#### G-Code Macros
- Add comments explaining complex logic
- Use descriptive variable names
- Include error handling
- Document macro parameters
- Test on real hardware when possible

**Example:**
```ini
[gcode_macro CALIBRATE_TOOL_XY]
description: Calibrate XY offsets for specified tool
# Parameters:
#   TOOL=<0-5>     : Tool number to calibrate (required)
#   SAMPLES=<n>    : Number of samples (default: 5)
#   TEMP=<temp>    : Calibration temperature (default: 180)
#
# This macro heats the tool, probes the NUDGE pin multiple times,
# calculates average offset, and updates the tool's XY offset.
gcode:
    # Validate parameters
    {% if params.TOOL is not defined %}
        {action_raise_error("TOOL parameter is required")}
    {% endif %}
    
    {% set tool_num = params.TOOL|int %}
    {% set samples = params.SAMPLES|default(5)|int %}
    {% set temp = params.TEMP|default(180)|int %}
    
    # Implementation...
```

### Testing Your Changes

**Before submitting:**
1. Test on actual hardware if possible
2. Test with example configuration
3. Check for Python syntax errors
4. Verify no breaking changes to existing functionality
5. Update documentation for new features
6. Add entries to CHANGELOG.md

**Testing Checklist:**
- [ ] Code runs without errors
- [ ] Feature works as intended
- [ ] No regressions in existing features
- [ ] Error handling works correctly
- [ ] Documentation updated
- [ ] Examples updated if needed

### Commit Messages

Write clear commit messages:

```bash
# Good commit messages
git commit -m "Fix: Prevent crash when tool detection fails during pickup"
git commit -m "Feature: Add automatic dock position learning macro"
git commit -m "Docs: Add troubleshooting section for Z-offset drift"

# Bad commit messages (avoid these)
git commit -m "fix stuff"
git commit -m "updates"
git commit -m "wip"
```

**Format:**
```
<type>: <short description>

<optional longer description>

<optional footer>
```

**Types:**
- `Feature:` - New feature
- `Fix:` - Bug fix
- `Docs:` - Documentation changes
- `Style:` - Formatting, no code change
- `Refactor:` - Code restructuring
- `Test:` - Adding tests
- `Chore:` - Maintenance tasks

### Pull Request Process

1. **Update your fork**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your changes**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Use the Pull Request template
   - Reference related issues
   - Describe changes clearly
   - Include testing information
   - Add screenshots/videos if relevant

4. **Review Process**
   - Maintainers will review your code
   - Address any requested changes
   - Be patient and respectful

5. **After Merge**
   - Delete your feature branch
   - Update your fork
   - Celebrate! 🎉

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tested on real hardware (if applicable)
- [ ] CHANGELOG.md updated
- [ ] Breaking changes documented

---

## 🧪 Testing Guidelines

### Hardware Testing

If you have access to toolchanger hardware:

1. **Test on non-production printer first**
2. **Start with slow speeds** for safety
3. **Monitor for unexpected behavior**
4. **Test error conditions** (intentional failures)
5. **Verify recovery procedures work**

### Safety First

- Never test unverified code on production printer
- Always have emergency stop ready
- Start with conservative parameters
- Test in safe, supervised environment
- Document any issues immediately

---

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

### Enforcement

Violations should be reported to project maintainers. All complaints will be reviewed and investigated.

---

## 📧 Contact

- **GitHub Issues:** For bugs and feature requests
- **GitHub Discussions:** For questions and general discussion
- **Email:** For private concerns

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the GPL-3.0 License.

---

## 🙏 Recognition

Contributors will be recognized in:
- CHANGELOG.md for their contributions
- GitHub contributors page
- Special thanks in release notes

---

Thank you for contributing to Klipper Toolchanger Extended! Your efforts help make multi-tool 3D printing more accessible and reliable for everyone.
