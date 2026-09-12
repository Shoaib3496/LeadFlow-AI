import { useEffect, useState } from "react";
import api from "../services/api";

import StatCard from "../components/StatCard";
import LeadTable from "../components/LeadTable";
import DashboardCharts from "../components/DashboardCharts";
import TopLeads from "../components/TopLeads";

function Dashboard() {

    const [loading, setLoading] = useState(true);

    const [leads, setLeads] = useState([]);
    const [topLeads, setTopLeads] = useState([]);
    const [topLeadsError, setTopLeadsError] = useState(false);
    const [leadsError, setLeadsError] = useState("");

    const [summary, setSummary] = useState({
        total_leads: 0,
        new_leads: 0,
        actionable_leads: 0,
        average_commercial_score: 0,
        best_commercial_score: 0,
        data_sources: 0,
        active_sources: 0,
        priority_distribution: {
            HOT: 0,
            WARM: 0,
            MEDIUM: 0,
            LOW: 0
        }
    });

    const [analytics, setAnalytics] = useState({
        sources: [],
        score_distribution: {},
        status_distribution: {}
    });

    async function loadDashboard() {

        setLoading(true);

        try {

            // Dashboard Summary
            const summaryResponse = await api.get("/dashboard/summary");
            setSummary(summaryResponse.data);

            // Dashboard Analytics
            const analyticsResponse = await api.get("/dashboard/analytics");
            setAnalytics(analyticsResponse.data);

            // Recent Leads
            try {

                setLeadsError("");

                const leadsResponse = await api.get("/leads", {
                    params: {
                        page: 1,
                        page_size: 5,
                        sort: "recent"
                    }
                });

                const recentLeads = Array.isArray(
                    leadsResponse.data?.items
                )
                    ? leadsResponse.data.items
                    : [];

                setLeads(recentLeads);

            } catch (error) {

                console.error(
                    "Failed to load recent leads:",
                    error
                );

                setLeads([]);

                setLeadsError(
                    "Unable to load recent leads."
                );
            }

            // Top Commercial Opportunities
            try {

                setTopLeadsError(false);

                const topLeadsResponse = await api.get("/top-leads");

                const topLeadData = Array.isArray(topLeadsResponse.data)
                    ? topLeadsResponse.data
                    : [];

                setTopLeads(topLeadData);

            } catch (error) {

                console.error("Failed to load top leads:", error);

                setTopLeads([]);
                setTopLeadsError(true);
            }

        } catch (error) {

            console.error("Failed to load dashboard:", error);

        } finally {

            setLoading(false);

        }

    }

    useEffect(() => {

        loadDashboard();

    }, []);

    if (loading) {

        return (

            <div className="flex justify-center items-center h-96">

                <div className="text-center">

                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto"></div>

                    <p className="mt-4 text-gray-600 font-medium">
                        Loading Dashboard...
                    </p>

                </div>

            </div>

        );

    }

    return (

        <div className="space-y-10">

            <div className="flex justify-between items-center mb-6">

                <div>

                    <h1 className="text-4xl font-bold tracking-tight text-gray-900">
                        LeadFlow AI Dashboard
                    </h1>

                    <p className="text-gray-500 mt-2 text-lg">
                        Monitor your AI-powered lead generation pipeline in real time.
                    </p>
                </div>

                <button
                    onClick={loadDashboard}
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50"
                >
                    {loading ? "Refreshing..." : "Refresh Dashboard"}
                </button>

            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">

                <StatCard
                    title="Total Leads"
                    value={summary.total_leads}
                    color="text-blue-600"
                    icon="📊"
                    subtitle="All stored opportunities"
                />

                <StatCard
                    title="Actionable Leads"
                    value={summary.actionable_leads}
                    color="text-green-600"
                    icon="🎯"
                    subtitle="Commercial score ≥ 40"
                />

                <StatCard
                    title="Average Commercial Score"
                    value={summary.average_commercial_score}
                    color="text-purple-600"
                    icon="⚡"
                    subtitle="Across all stored leads"
                />

                <StatCard
                    title="Lead Platforms"
                    value={summary.data_sources}
                    color="text-orange-600"
                    icon="🌐"
                    subtitle="Platforms represented in collected leads"
                />

            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                <StatCard
                    title="Best Commercial Score"
                    value={summary.best_commercial_score}
                    color="text-emerald-600"
                    icon="🏆"
                    subtitle="Highest ranked opportunity"
                />

                <StatCard
                    title="New CRM Leads"
                    value={summary.new_leads}
                    color="text-cyan-600"
                    icon="🆕"
                    subtitle="Leads currently marked New"
                />

                <StatCard
                    title="Enabled Sources"
                    value={summary.active_sources}
                    color="text-indigo-600"
                    icon="📡"
                    subtitle="Sources enabled for collection"
                />

            </div>

            <div>

                <div className="mb-5">

                    <h2 className="text-2xl font-bold text-gray-900">
                        Commercial Priority Distribution
                    </h2>

                    <p className="text-gray-500 mt-1">
                        AI-ranked opportunities grouped by commercial priority.
                    </p>

                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">

                    <StatCard
                        title="Hot Leads"
                        value={summary.priority_distribution?.HOT ?? 0}
                        color="text-red-600"
                        icon="🔥"
                        subtitle="Highest priority opportunities"
                    />

                    <StatCard
                        title="Warm Leads"
                        value={summary.priority_distribution?.WARM ?? 0}
                        color="text-orange-500"
                        icon="🟡"
                        subtitle="Strong commercial opportunities"
                    />

                    <StatCard
                        title="Medium Leads"
                        value={summary.priority_distribution?.MEDIUM ?? 0}
                        color="text-blue-600"
                        icon="🔵"
                        subtitle="Potential opportunities"
                    />

                    <StatCard
                        title="Low Leads"
                        value={summary.priority_distribution?.LOW ?? 0}
                        color="text-gray-600"
                        icon="⚪"
                        subtitle="Low-priority opportunities"
                    />

                </div>

            </div>

            <div className="mt-4 text-sm text-gray-500">

                Classified leads:{" "}

                <span className="font-semibold text-gray-700">

                    {(summary.priority_distribution?.HOT ?? 0) +
                    (summary.priority_distribution?.WARM ?? 0) +
                    (summary.priority_distribution?.MEDIUM ?? 0) +
                    (summary.priority_distribution?.LOW ?? 0)}

                </span>

                {" / "}

                <span className="font-semibold text-gray-700">
                    {summary.total_leads}
                </span>

            </div>

            <div className="bg-white rounded-2xl shadow-lg p-6">
                <DashboardCharts analytics={analytics} />
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-6">
                <TopLeads
                    leads={topLeads}
                    error={topLeadsError}
                />
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-6">

                {leadsError ? (

                    <div className="py-12 text-center">

                        <div className="text-4xl mb-3">
                            ⚠️
                        </div>

                        <h3 className="text-lg font-semibold text-gray-800">
                            Recent leads unavailable
                        </h3>

                        <p className="text-gray-500 mt-2">
                            {leadsError}
                        </p>

                        <button
                            onClick={loadDashboard}
                            className="
                                mt-5
                                px-5
                                py-2
                                bg-blue-600
                                text-white
                                rounded-lg
                                font-semibold
                                hover:bg-blue-700
                                transition
                            "
                        >
                            Retry
                        </button>

                    </div>

                ) : leads.length === 0 ? (

                    <div className="py-12 text-center">

                        <div className="text-4xl mb-3">
                            📭
                        </div>

                        <h3 className="text-lg font-semibold text-gray-800">
                            No leads available
                        </h3>

                        <p className="text-gray-500 mt-2">
                            New leads will appear here after the collection pipeline runs.
                        </p>

                    </div>

                ) : (

                    <LeadTable leads={leads} />

                )}

            </div>

        </div>

    );

}

export default Dashboard;