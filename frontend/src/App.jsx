import { Routes, Route } from "react-router-dom";

import DashboardLayout from "./layouts/DashboardLayout";

import Dashboard from "./pages/Dashboard";
import Leads from "./pages/Leads";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import LeadDetails from "./pages/LeadDetails";
import Sources from "./pages/Sources";
import ScraperManager from "./pages/ScraperManager";

function App() {

    return (

        <DashboardLayout>

            <Routes>

                <Route
                    path="/"
                    element={<Dashboard />}
                />

                <Route
                    path="/leads"
                    element={<Leads />}
                />

                <Route
                    path="/lead/:id"
                    element={<LeadDetails />}
                />

                <Route
                    path="/analytics"
                    element={<Analytics />}
                />

                <Route
                    path="/sources"
                    element={<Sources />}
                />

                <Route
                    path="/settings"
                    element={<Settings />}
                />

                <Route
                    path="/scraper"
                    element={<ScraperManager />}
                />

            </Routes>

        </DashboardLayout>

    );

}

export default App;