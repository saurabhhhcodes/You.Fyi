# Implementation Plan - Modern UI Overhaul

The goal is to elevate the UI to a "professionally modern" standard, suitable for production. We will focus on aesthetics (typography, spacing, colors) and usability (feedback, interactions).

## User Review Required
> [!NOTE]
> I will be adding a CDN link for the 'Inter' font to `index.html` to ensure consistent typography.

## Proposed Changes

### 1. Visual Design (`app/static/style.css`)
- **Typography**: Import 'Inter' from Google Fonts. Refine font weights and line heights.
- **Color Palette**: Switch to a sophisticated Slate/Zinc palette.
    - Background: `#f8fafc` (Slate 50)
    - Surface: `#ffffff`
    - Primary: `#2563eb` (Blue 600) -> `#1d4ed8` (Blue 700)
    - Text: `#0f172a` (Slate 900) / `#64748b` (Slate 500)
    - Borders: `#e2e8f0` (Slate 200)
- **Components**:
    - **Buttons**: Subtle shadows, smooth transitions, focus rings.
    - **Inputs**: Clean borders, focus rings matching primary color.
    - **Table**: Refined spacing, sticky header, subtle hover states.
    - **Sidebar**: Refine active states and spacing.
- **Animations**: Add slide-in/fade-in animations for panels and toasts.

### 2. Structure (`app/static/index.html`)
- Add Google Fonts link.
- Add a container for Toast notifications.
- Ensure semantic structure is maintained.

### 3. Logic & UX (`app/static/app.js`)
- **Toast System**: Replace `alert()` and `console.log` with a custom `showToast(msg, type)` function.
- **Loading States**: Add visual feedback (spinners or disabled states) to buttons during async operations.
- **Empty States**: Ensure empty states look good (already partially there, will refine).

## Verification Plan
- **Visual Check**: Verify the look and feel matches modern standards (clean, spacious, consistent).
- **Interaction Check**: Test hover states, focus states, and transitions.
- **Functionality**: Ensure the new Toast system works for success and error messages.
