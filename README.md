# FME Intervention Tracker Dashboard

A comprehensive web application for tracking Field Maintenance Engineer (FME) interventions on telecom sites.

## 🚀 Features

- **Intervention Logging**: Capture FME details, site information, and initial state with automatic timestamps
- **Closure Management**: Record final state and departure time for completed interventions
- **Real-time Dashboard**: Monitor ongoing interventions and view key metrics
- **Advanced Analytics**: Interactive charts by company, initial state, and action type
- **Smart Filtering**: Filter by status, company, unresolved sites, and date range
- **Custom Actions**: Add and manage custom intervention actions
- **Local Database**: SQLite storage with no external dependencies

## 📋 Requirements

- Python 3.8+
- Modern web browser (Chrome, Firefox, Edge, Safari)

## 🔧 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install Flask==3.0.0 flask-cors==4.0.0
```

### Launch

```bash
python app.py
```

Access the dashboard at `http://localhost:5000`

## 💾 Database

SQLite database `fme_tracker.db` is auto-created on first run.

**Key Tables:**
- `interventions`: FME details, site info, timestamps, status
- `custom_actions`: User-defined intervention types

## 📱 Usage Guide

| Task | Steps |
|------|-------|
| **New Intervention** | Click "Nouvelle" → Fill form → Save |
| **Close Intervention** | Select intervention → Click "Fermer" → Set final state |
| **Add Action** | Click "+" in action field → Enter name |
| **Filter Data** | Go to "Interventions" → Apply filters → Click "Filtrer" |
| **View Stats** | Click "Statistiques" → Review charts |

## 🎨 UI Highlights

- Modern dark design with orange accents
- Fully responsive layout
- Auto-refresh every 30 seconds
- Intuitive navigation menu

## 🔒 Security

- ✅ Local database only
- ✅ No internet required
- ✅ No external dependencies
- ✅ Data stays on device

## ⚙️ Customization

**Change predefined actions** in `app.py`:
```python
PREDEFINED_ACTIONS = ["Action 1", "Action 2"]
```

**Change port**:
```python
app.run(debug=True, port=8080)
```

## 📊 Performance

- Handles 15-20 daily interventions
- Supports thousands of historical records
- Multi-user capable

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Server won't start | Check Python version, reinstall dependencies |
| Page not loading | Verify server is running, clear browser cache |
| Data missing | Check browser console (F12), restart server |

## 🚀 Future Enhancements

- Excel/PDF exports
- Email/SMS notifications
- Mobile app
- Multi-user authentication
- WebSocket real-time updates

---

**Efficient FME intervention tracking for telecom sites** 📡
