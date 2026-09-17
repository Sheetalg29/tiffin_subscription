# Architecture

```text
                   React / Vite
                        |
                     REST/JSON
                        |
                    FastAPI
          _____________|______________
         |             |              |
       Auth        CRUD services   Billing service
         |             |              |
         |             |              |
         +-------------+--------------+
                       |
                   SQLAlchemy
                       |
                  PostgreSQL
```

The browser never performs authoritative billing calculations. The backend owns business rules and returns the calculated bill to the UI.
