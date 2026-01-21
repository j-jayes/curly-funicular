# Frontend Improvements Checklist

**Started**: 2026-01-21  
**Status**: In Progress - Testing

## Overview

Improving the Swedish Labor Market Analytics Platform frontend with:
- Multi-select occupation filtering
- Fixed map showing weighted average income by region
- Redesigned salary scatter plot (men vs women median)
- Clear visual separation between income stats (SCB) and job ads (Arbetsförmedlingen)
- Better use of job ads data (top employers, etc.)

---

## Tasks

### Phase 1: API Updates
- [x] Update income API to support multi-occupation filtering (comma-separated)
- [x] Update jobs API to support multi-occupation filtering
- [x] Add endpoint for top employers from job ads data
- [x] Test API changes locally

### Phase 2: Frontend Filter Updates
- [x] Change FilterPanel occupation dropdown to multi-select with checkboxes
- [x] Update App.jsx state management for selectedOccupations (array)
- [x] Update api.js to send comma-separated occupation codes

### Phase 3: Map Visualization
- [x] Fix map to show weighted average income (by employee count) per region
- [x] Update hover tooltip to show employee count used in weighting
- [ ] Test map with multiple occupation selections

### Phase 4: Salary Scatter Plot
- [x] Replace IncomeBoxPlot with scatter plot (men median x-axis, women median y-axis)
- [x] Add diagonal reference line for gender parity
- [x] Add tooltips with occupation name, SSYK code, and both salary values
- [x] Add note about national-only dispersion data

### Phase 5: Visual Separation & Job Ads Insights
- [x] Create section headers distinguishing SCB vs Arbetsförmedlingen data
- [x] Add icons and subtle background colors for each section
- [x] Create new component for top employers visualization
- [x] Integrate top employers into jobs section

### Phase 6: Testing & Polish
- [x] Docker compose build (API and frontend)
- [x] Services running on localhost
- [ ] Verify all filters work correctly in browser
- [ ] Check responsive layout
- [ ] Final review before GCP deployment

---

## Notes

- Dispersion data (P10-P90) is national only, no regional breakdown
- Income data uses SSYK 2012 4-digit codes
- Map uses NUTS-2 regions from Eurostat GeoJSON
- Weighted average uses `num_employees` field from SCB income data

---

## Progress Log

### 2026-01-21
- Created checklist
- Researched codebase structure
- Updated API database.py for multi-occupation support
- Updated API routes (income.py, jobs.py) for comma-separated occupations
- Added TopEmployer schema and /jobs/top-employers endpoint
- Updated FilterPanel.jsx with multi-select checkboxes
- Updated App.jsx with new state management and visual separation
- Updated api.js service with formatOccupations helper
- Fixed SwedenMap.jsx to show weighted average income
- Created GenderScatterPlot.jsx (scatter plot for men vs women median)
- Created TopEmployersChart.jsx (horizontal bar chart of top employers)
- Docker compose build successful
- Services running on localhost:3000 (frontend) and localhost:8000 (API)
