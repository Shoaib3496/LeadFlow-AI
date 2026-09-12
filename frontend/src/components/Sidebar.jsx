import { NavLink } from "react-router-dom";

function Sidebar() {

    const linkClass = ({ isActive }) =>
        `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 font-medium ${
            isActive
                ? "bg-blue-600 text-white shadow-lg"
                : "text-gray-300 hover:bg-slate-800 hover:text-white"
        }`;

    return (

        <aside className="w-72 min-h-screen bg-slate-900 text-white flex flex-col shadow-2xl">

            {/* Logo */}

            <div className="px-6 py-8 border-b border-slate-800">

                <h1 className="text-3xl font-bold tracking-wide">

                    🚀 LeadFlow AI

                </h1>

                <p className="text-slate-400 text-sm mt-2">

                    AI Lead Discovery Platform

                </p>

            </div>

            {/* Navigation */}

            <nav className="flex-1 px-5 py-6 space-y-3">

                <NavLink
                    to="/"
                    end
                    className={linkClass}
                >
                    <span className="text-xl">📊</span>
                    Dashboard
                </NavLink>

                <NavLink
                    to="/leads"
                    className={linkClass}
                >
                    <span className="text-xl">📋</span>
                    Leads
                </NavLink>

                <NavLink
                    to="/analytics"
                    className={linkClass}
                >
                    <span className="text-xl">📈</span>
                    Analytics
                </NavLink>

                <NavLink
                    to="/sources"
                    className={linkClass}
                >
                    <span className="text-xl">🌐</span>
                    Sources
                </NavLink>

                <NavLink
                    to="/scraper"
                    className={linkClass}
                >
                    <span className="text-xl">🕷</span>
                    Scraper Manager
                </NavLink>

                <NavLink
                    to="/settings"
                    className={linkClass}
                >
                    <span className="text-xl">⚙️</span>
                    Settings
                </NavLink>

            </nav>

            {/* Footer */}

            <div className="border-t border-slate-800 p-6">

                <div className="bg-slate-800 rounded-xl p-4">

                    <p className="text-sm text-slate-300">

                        LeadFlow AI

                    </p>

                    <p className="text-xs text-slate-500 mt-1">

                        Version 1.0.0

                    </p>

                </div>

            </div>

        </aside>

    );

}

export default Sidebar;