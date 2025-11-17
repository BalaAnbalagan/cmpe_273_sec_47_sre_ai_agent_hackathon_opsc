# Frontend Update: Violations Dialog

## Changes Made

### 1. Created ViolationsDialog Component
- **File:** `frontend/components/ViolationsDialog.tsx`
- **Purpose:** Display safety violation images in a modal/dialog
- **Features:**
  - Fetches violations from `/sre/images/safety-analysis` endpoint
  - Shows violation images in a grid
  - Click to view image details
  - AI analysis summary

### 2. Updates Needed in `frontend/app/page.tsx`

Add these changes to enable the violations dialog:

#### Step 1: Add import at the top (after line 3)
```typescript
import ViolationsDialog from '@/components/ViolationsDialog';
```

#### Step 2: Add state variables (after line 44)
```typescript
const [showViolationsDialog, setShowViolationsDialog] = useState(false);
```

#### Step 3: Update the Safety Compliance CapabilityCard (around line 277)

**Replace:**
```typescript
<CapabilityCard
  title="Safety Compliance Analysis"
  description="AI-powered safety violation detection and scoring"
  example="Real-time compliance monitoring across all sites"
/>
```

**With:**
```typescript
<button
  onClick={() => setShowViolationsDialog(true)}
  className="w-full text-left"
>
  <CapabilityCard
    title="Safety Compliance Analysis"
    description="AI-powered safety violation detection and scoring"
    example="Real-time compliance monitoring across all sites - CLICK TO VIEW VIOLATIONS"
  />
</button>
```

#### Step 4: Add the dialog component (before the closing `</div>` of main, around line 294)
```typescript
{/* Violations Dialog */}
<ViolationsDialog
  isOpen={showViolationsDialog}
  onClose={() => setShowViolationsDialog(false)}
  apiUrl={activeZone === 'az1' ? API_AZ1 : API_AZ2}
/>
```

## How It Works

1. User clicks on "Safety Compliance Analysis" card
2. Dialog opens and fetches violations from backend
3. Backend returns violation images with URLs
4. Dialog displays images in a grid
5. Click on any image to see full details
6. AI analysis summary shown at the top

## Backend Changes

The backend endpoint `/sre/images/safety-analysis` now returns:
- `violation_images`: Array of violation images with URLs
- Each image includes:
  - `image_id`: Unique identifier
  - `site_id`: Site location
  - `description`: Violation description
  - `url`: Full-size image URL
  - `thumbnail_url`: Thumbnail URL
  - `timestamp`: When detected
  - `violation_type`: Type of violation

## Testing

1. Start local frontend: `npm run dev`
2. Navigate to http://localhost:3001
3. Click on "Safety Compliance Analysis" card
4. Dialog should open showing violation images
5. Click on any image to see details

## Notes

- Currently using placeholder images (`placehold.co`)
- Replace URLs with real blob storage URLs when images are uploaded
- The dialog is fully responsive and mobile-friendly
- Includes loading states and error handling
