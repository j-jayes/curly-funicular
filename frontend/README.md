# React Frontend

This is the React-based frontend for the Swedish Labor Market Analytics platform.

## Features

- Interactive map of Sweden showing data by region
- Charts for income spread visualization
- Charts for number of jobs visualization
- Filters for:
  - Occupation
  - Age group
  - Gender
  - Location/Region

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── Map/
│   │   │   └── SwedenMap.jsx
│   │   ├── Charts/
│   │   │   ├── IncomeChart.jsx
│   │   │   └── JobsChart.jsx
│   │   ├── Filters/
│   │   │   └── FilterPanel.jsx
│   │   └── Layout/
│   │       ├── Header.jsx
│   │       └── Footer.jsx
│   ├── services/
│   │   └── api.js
│   ├── App.jsx
│   ├── App.css
│   ├── index.js
│   └── index.css
├── package.json
├── Dockerfile
└── README.md
```

## Setup

```bash
npm install
```

## Run Locally

```bash
npm start
```

The application will open at http://localhost:3000

## Build for Production

```bash
npm run build
```

## Environment Variables

Create a `.env` file:

```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Technologies

- React 18
- Recharts for data visualization
- D3.js for map visualization
- Axios for API calls
- Material-UI for UI components
