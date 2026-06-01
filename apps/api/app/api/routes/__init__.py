from app.api.routes import auth, catalog, export, jobs, opportunities, risk

routers = [
    auth.router,
    opportunities.router,
    catalog.router,
    risk.router,
    export.router,
    jobs.router,
]
