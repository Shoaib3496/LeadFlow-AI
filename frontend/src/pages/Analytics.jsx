import { useEffect, useState } from "react";
import api from "../services/api";

import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid
} from "recharts";

const COLORS = [
    "#dc2626",
    "#f59e0b",
    "#2563eb",
    "#6b7280",
    "#16a34a",
    "#7c3aed",
    "#0891b2",
    "#9333ea"
];

function Analytics() {

    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        loadAnalytics();
    }, []);

    async function loadAnalytics() {
        try {
            setLoading(true);
            setError("");

            const response = await api.get("/dashboard/analytics");

            console.log("Analytics API Response:", response.data);

            setAnalytics(response.data);

        } catch (error) {
            console.error("Analytics Error:", error);
            setError("Unable to load analytics data.");
        } finally {
            setLoading(false);
        }
    }

    // =====================================================
    // LOADING STATE
    // =====================================================

    if (loading) {
        return (
            <div className="p-6">
                <h1 className="text-3xl font-bold mb-8">
                    Analytics Dashboard
                </h1>

                <div className="bg-white rounded-xl shadow p-10 text-center">
                    <p className="text-gray-500">
                        Loading analytics...
                    </p>
                </div>
            </div>
        );
    }

    // =====================================================
    // ERROR STATE
    // =====================================================

    if (error || !analytics) {
        return (
            <div className="p-6">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold">
                        Analytics Dashboard
                    </h1>

                    <button
                        onClick={loadAnalytics}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg transition"
                    >
                        Retry
                    </button>
                </div>

                <div className="bg-white rounded-xl shadow p-10 text-center">
                    <p className="text-red-600">
                        {error || "No analytics data available."}
                    </p>
                </div>
            </div>
        );
    }

    // =====================================================
    // BACKEND ANALYTICS DATA
    // =====================================================

    const totalLeads = analytics.total_leads || 0;

    const actionableLeads =
        analytics.actionable_leads || 0;

    const actionableRate =
        analytics.actionable_rate || 0;

    const averageCommercialScore =
        analytics.average_commercial_score || 0;

    const bestCommercialScore =
        analytics.best_commercial_score || 0;

    const priorityDistribution =
        analytics.priority_distribution || {};

    const sourcePerformance =
        analytics.source_performance || [];

    const serviceDistribution =
        analytics.service_distribution || [];

    // =====================================================
    // PRIORITY DATA
    // =====================================================

    const priorityData = [
        {
            name: "HOT",
            value: priorityDistribution.HOT || 0
        },
        {
            name: "WARM",
            value: priorityDistribution.WARM || 0
        },
        {
            name: "MEDIUM",
            value: priorityDistribution.MEDIUM || 0
        },
        {
            name: "LOW",
            value: priorityDistribution.LOW || 0
        }
    ];

    // =====================================================
    // SERVICE DATA
    // =====================================================

    const serviceData = serviceDistribution.map((item) => ({
        name: item.service || "Unknown",
        count: item.count || 0
    }));

    // =====================================================
    // SOURCE DATA
    // =====================================================

    const sourceData = sourcePerformance.map((item) => ({
        name: item.platform || "Unknown",
        total: item.total || 0,
        actionable: item.actionable || 0,
        conversion_rate: item.conversion_rate || 0
    }));

    // =====================================================
    // RETURN UI
    // =====================================================

    return (
        <div className="p-6 space-y-8">

            {/* =================================================
                HEADER
            ================================================= */}

            <div className="flex justify-between items-center">

                <div>
                    <h1 className="text-3xl font-bold text-gray-900">
                        Analytics Dashboard
                    </h1>

                    <p className="text-gray-500 mt-2">
                        Commercial intelligence and lead-generation
                        performance.
                    </p>
                </div>

                <button
                    onClick={loadAnalytics}
                    disabled={loading}
                    className="
                        bg-blue-600
                        hover:bg-blue-700
                        text-white
                        px-5
                        py-2
                        rounded-lg
                        transition
                        disabled:opacity-50
                    "
                >
                    🔄 Refresh
                </button>

            </div>


            {/* =================================================
                KPI CARDS
            ================================================= */}

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">

                {/* Total Leads */}

                <div className="bg-white rounded-2xl shadow border border-gray-100 p-6">
                    <p className="text-sm text-gray-500">
                        Total Leads
                    </p>

                    <h2 className="text-3xl font-bold text-blue-600 mt-2">
                        {totalLeads}
                    </h2>

                    <p className="text-xs text-gray-400 mt-2">
                        All stored opportunities
                    </p>
                </div>


                {/* Actionable Leads */}

                <div className="bg-white rounded-2xl shadow border border-gray-100 p-6">
                    <p className="text-sm text-gray-500">
                        Actionable Leads
                    </p>

                    <h2 className="text-3xl font-bold text-green-600 mt-2">
                        {actionableLeads}
                    </h2>

                    <p className="text-xs text-gray-400 mt-2">
                        Commercial score ≥ 40
                    </p>
                </div>


                {/* Actionable Rate */}

                <div className="bg-white rounded-2xl shadow border border-gray-100 p-6">
                    <p className="text-sm text-gray-500">
                        Actionable Rate
                    </p>

                    <h2 className="text-3xl font-bold text-purple-600 mt-2">
                        {actionableRate}%
                    </h2>

                    <p className="text-xs text-gray-400 mt-2">
                        Percentage of actionable leads
                    </p>
                </div>


                {/* Average Score */}

                <div className="bg-white rounded-2xl shadow border border-gray-100 p-6">
                    <p className="text-sm text-gray-500">
                        Average Commercial Score
                    </p>

                    <h2 className="text-3xl font-bold text-orange-600 mt-2">
                        {averageCommercialScore}
                    </h2>

                    <p className="text-xs text-gray-400 mt-2">
                        Across all stored leads
                    </p>
                </div>

            </div>


            {/* =================================================
                SECONDARY KPI CARDS
            ================================================= */}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Best Score */}

                <div className="bg-white rounded-2xl shadow border border-gray-100 p-6">
                    <p className="text-sm text-gray-500">
                        Best Commercial Score
                    </p>

                    <h2 className="text-3xl font-bold text-emerald-600 mt-2">
                        {bestCommercialScore}
                    </h2>

                    <p className="text-xs text-gray-400 mt-2">
                        Highest ranked opportunity
                    </p>
                </div>


                {/* Actionable vs Total */}

                <div className="bg-white rounded-2xl shadow border border-gray-100 p-6">

                    <p className="text-sm text-gray-500">
                        Lead Quality
                    </p>

                    <div className="flex items-end gap-2 mt-2">

                        <h2 className="text-3xl font-bold text-indigo-600">
                            {actionableLeads}
                        </h2>

                        <span className="text-gray-400 mb-1">
                            / {totalLeads}
                        </span>

                    </div>

                    <p className="text-xs text-gray-400 mt-2">
                        Actionable opportunities out of total leads
                    </p>

                </div>

            </div>


            {/* =================================================
                PRIORITY + SOURCE PERFORMANCE
            ================================================= */}

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">


                {/* =================================================
                    PRIORITY DISTRIBUTION
                ================================================= */}

                <div className="bg-white rounded-2xl shadow border border-gray-100 p-6">

                    <h2 className="text-xl font-bold text-gray-900">
                        Commercial Priority Distribution
                    </h2>

                    <p className="text-sm text-gray-500 mt-1">
                        AI-ranked opportunities by commercial priority.
                    </p>

                    <ResponsiveContainer
                        width="100%"
                        height={350}
                    >

                        <PieChart>

                            <Pie
                                data={priorityData}
                                dataKey="value"
                                nameKey="name"
                                cx="50%"
                                cy="50%"
                                outerRadius={120}
                                label
                            >

                                {priorityData.map(
                                    (entry, index) => (
                                        <Cell
                                            key={entry.name}
                                            fill={
                                                COLORS[
                                                    index %
                                                    COLORS.length
                                                ]
                                            }
                                        />
                                    )
                                )}

                            </Pie>

                            <Tooltip />

                            <Legend />

                        </PieChart>

                    </ResponsiveContainer>

                </div>


                {/* =================================================
                    SOURCE PERFORMANCE
                ================================================= */}

                <div className="bg-white rounded-2xl shadow border border-gray-100 p-6">

                    <h2 className="text-xl font-bold text-gray-900">
                        Source Performance
                    </h2>

                    <p className="text-sm text-gray-500 mt-1">
                        Lead volume and actionable opportunities by source.
                    </p>

                    <ResponsiveContainer
                        width="100%"
                        height={350}
                    >

                        <BarChart
                            data={sourceData}
                            margin={{
                                top: 10,
                                right: 20,
                                left: 0,
                                bottom: 60
                            }}
                        >

                            <CartesianGrid
                                strokeDasharray="3 3"
                            />

                            <XAxis
                                dataKey="name"
                                angle={-35}
                                textAnchor="end"
                                interval={0}
                            />

                            <YAxis />

                            <Tooltip />

                            <Legend />

                            <Bar
                                dataKey="total"
                                name="Total Leads"
                                fill="#2563eb"
                            />

                            <Bar
                                dataKey="actionable"
                                name="Actionable"
                                fill="#16a34a"
                            />

                        </BarChart>

                    </ResponsiveContainer>

                </div>

            </div>


            {/* =================================================
                SERVICE DISTRIBUTION
            ================================================= */}

            <div className="bg-white rounded-2xl shadow border border-gray-100 p-6">

                <h2 className="text-xl font-bold text-gray-900">
                    Service Demand
                </h2>

                <p className="text-sm text-gray-500 mt-1 mb-6">
                    Services most frequently identified across collected
                    opportunities.
                </p>

                {serviceData.length === 0 ? (

                    <div className="py-12 text-center text-gray-500">
                        No service distribution data available.
                    </div>

                ) : (

                    <ResponsiveContainer
                        width="100%"
                        height={400}
                    >

                        <BarChart
                            data={serviceData}
                            layout="vertical"
                            margin={{
                                top: 10,
                                right: 30,
                                left: 80,
                                bottom: 10
                            }}
                        >

                            <CartesianGrid
                                strokeDasharray="3 3"
                            />

                            <XAxis
                                type="number"
                            />

                            <YAxis
                                type="category"
                                dataKey="name"
                                width={120}
                            />

                            <Tooltip />

                            <Bar
                                dataKey="count"
                                name="Leads"
                                fill="#7c3aed"
                            />

                        </BarChart>

                    </ResponsiveContainer>

                )}

            </div>


            {/* =================================================
                SOURCE PERFORMANCE TABLE
            ================================================= */}

            <div className="bg-white rounded-2xl shadow border border-gray-100 p-6">

                <div className="mb-5">

                    <h2 className="text-xl font-bold text-gray-900">
                        Source Performance Details
                    </h2>

                    <p className="text-sm text-gray-500 mt-1">
                        Compare lead quality across collection platforms.
                    </p>

                </div>

                <div className="overflow-x-auto">

                    <table className="w-full">

                        <thead className="bg-gray-50">

                            <tr className="text-left text-xs uppercase tracking-wider text-gray-500">

                                <th className="p-4">
                                    Platform
                                </th>

                                <th className="p-4">
                                    Total
                                </th>

                                <th className="p-4">
                                    Actionable
                                </th>

                                <th className="p-4">
                                    Actionable Rate
                                </th>

                            </tr>

                        </thead>

                        <tbody>

                            {sourceData.map((source) => (

                                <tr
                                    key={source.name}
                                    className="border-t hover:bg-gray-50"
                                >

                                    <td className="p-4 font-medium text-gray-800">
                                        {source.name}
                                    </td>

                                    <td className="p-4 text-gray-600">
                                        {source.total}
                                    </td>

                                    <td className="p-4 font-semibold text-green-600">
                                        {source.actionable}
                                    </td>

                                    <td className="p-4">

                                        <span
                                            className={`
                                                inline-flex
                                                px-3
                                                py-1
                                                rounded-full
                                                text-sm
                                                font-medium
                                                ${
                                                    source.conversion_rate >= 40
                                                        ? "bg-green-100 text-green-700"
                                                        : source.conversion_rate >= 10
                                                        ? "bg-yellow-100 text-yellow-700"
                                                        : "bg-gray-100 text-gray-600"
                                                }
                                            `}
                                        >
                                            {source.conversion_rate}%
                                        </span>

                                    </td>

                                </tr>

                            ))}

                        </tbody>

                    </table>

                </div>

            </div>

        </div>
    );
}

export default Analytics;