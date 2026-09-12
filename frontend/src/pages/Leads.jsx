import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../services/api";

function Leads() {

    const [loading, setLoading] = useState(true);
    const [leads, setLeads] = useState([]);

    const [search, setSearch] = useState("");
    const [platform, setPlatform] = useState("");
    const [status, setStatus] = useState("");
    const [opportunityStatus, setOpportunityStatus] = useState("");
    const [minScore, setMinScore] = useState(0);
    const [sort, setSort] = useState("score_desc");

    const [page, setPage] = useState(1);
    const [pageSize] = useState(10);
    const [total, setTotal] = useState(0);

    const loadLeads = async () => {

        setLoading(true);

        try {

            const response = await api.get("/leads", {
                params: {
                    search,
                    platform,
                    status,
                    opportunity_status: opportunityStatus,
                    min_score: minScore,
                    sort,
                    page,
                    page_size: pageSize
                }
            });

            setLeads(response.data.items);
            setTotal(response.data.total);

        } catch (error) {

            console.error("Error loading leads:", error);

        } finally {

            setLoading(false);

        }

    };

    useEffect(() => {

        loadLeads();

    }, [search, platform, status, minScore, opportunityStatus, sort, page, pageSize]);

    useEffect(() => {

        setPage(1);

    }, [search, platform, status, opportunityStatus, minScore, sort]);

    const resetFilters = () => {

        setSearch("");
        setPlatform("");
        setStatus("");
        setOpportunityStatus("");
        setMinScore(0);
        setSort("score_desc");
        setPage(1);

    };

    const refreshLeads = () => {

        loadLeads();

    };

    const totalPages = Math.max(1, Math.ceil(total / pageSize));

    const startLead =
        total === 0 ? 0 : (page - 1) * pageSize + 1;

    const endLead =
        Math.min(page * pageSize, total);

    return (

        <div>

            <div className="flex justify-between items-center mb-2">

                <h1 className="text-3xl font-bold">
                    Leads
                </h1>

                <button
                    onClick={refreshLeads}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg transition"
                >
                    🔄 Refresh
                </button>

            </div>

            <p className="text-gray-500 mb-6">
                Total Leads: <strong>{total}</strong>
            </p>

            {/* Filters */}

            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 mb-6">

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-4 items-end">

                    <input
                        type="text"
                        placeholder="Search leads..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="border rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                    />

                    <select
                        value={platform}
                        onChange={(e) => setPlatform(e.target.value)}
                        className="border rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                    >
                        <option value="">All Platforms</option>
                        <option value="Dev.to">Dev.to</option>
                        <option value="Freelancer">Freelancer</option>
                        <option value="GitHub">GitHub</option>
                        <option value="Hacker News">Hacker News</option>
                        <option value="Product Hunt">Product Hunt</option>
                        <option value="RemoteOK">RemoteOK</option>
                    </select>

                    <select
                        value={status}
                        onChange={(e) => setStatus(e.target.value)}
                        className="border rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                    >
                        <option value="">All Status</option>
                        <option value="New">New</option>
                        <option value="Contacted">Contacted</option>
                        <option value="Meeting Scheduled">Meeting Scheduled</option>
                        <option value="Proposal Sent">Proposal Sent</option>
                        <option value="Won">Won</option>
                        <option value="Lost">Lost</option>
                    </select>

                    <select
                        value={opportunityStatus}
                        onChange={(e) => setOpportunityStatus(e.target.value)}
                        className="border rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                    >
                        <option value="">All Opportunities</option>
                        <option value="OPEN">Open</option>
                        <option value="CLOSED">Closed</option>
                        <option value="EXPIRED">Expired</option>
                        <option value="REMOVED">Removed</option>
                        <option value="UNKNOWN">Unknown</option>
                    </select>

                    <select
                        value={minScore}
                        onChange={(e) => setMinScore(Number(e.target.value))}
                        className="border rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                    >
                        <option value="0">All Scores</option>
                        <option value="50">50+</option>
                        <option value="70">70+</option>
                        <option value="80">80+</option>
                        <option value="90">90+</option>
                    </select>

                    <select
                        value={sort}
                        onChange={(e) => setSort(e.target.value)}
                        className="border rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:outline-none transition"
                    >
                        <option value="score_desc">Highest Score</option>
                        <option value="score_asc">Lowest Score</option>
                        <option value="title_asc">Title (A-Z)</option>
                        <option value="title_desc">Title (Z-A)</option>
                    </select>

                    <button
                        onClick={resetFilters}
                        className="bg-gray-100 hover:bg-gray-200 rounded-lg px-5 py-3 font-medium transition"
                    >
                        Reset
                    </button>

                    <button
                        onClick={refreshLeads}
                        className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-5 py-3 font-medium transition shadow"
                    >
                        Refresh
                    </button>

                </div>

            </div>

            {/* Leads Table */}

            <div className="bg-white rounded-xl shadow overflow-hidden">

                <div className="overflow-x-auto">

                    <table className="w-full">

                        <thead className="bg-gray-100">

                            <tr>

                                <th className="p-4 text-left">Commercial Score</th>
                                <th className="p-4 text-center">Intent</th>
                                <th className="p-4 text-center">Fit</th>
                                <th className="p-4 text-center">Qualification</th>
                                <th className="p-4 text-left">Priority</th>
                                <th className="p-4 text-left">Title</th>
                                <th className="p-4 text-left">Service</th>
                                <th className="p-4 text-left">Budget</th>
                                <th className="p-4 text-center">Bids</th>
                                <th className="p-4 text-center">Type</th>
                                <th className="p-4 text-center">Urgent</th>
                                <th className="p-4 text-left">Source</th>
                                <th className="p-4 text-left">CRM Status</th>
                                <th className="p-4 text-left">Opportunity</th>
                                <th className="p-4 text-left">Last Checked</th>
                                <th className="p-4 text-left">Action</th>

                            </tr>

                        </thead>

                        <tbody>

                            {loading ? (

                                [...Array(5)].map((_, index) => (

                                    <tr key={index} className="border-b">

                                        <td className="p-4">
                                            <div className="h-8 w-14 bg-gray-200 rounded-full animate-pulse"></div>
                                        </td>

                                        <td className="p-4">
                                            <div className="h-5 w-64 bg-gray-200 rounded animate-pulse"></div>
                                        </td>

                                        <td className="p-4">
                                            <div className="h-5 w-32 bg-gray-200 rounded animate-pulse"></div>
                                        </td>

                                        <td className="p-4">
                                            <div className="h-5 w-28 bg-gray-200 rounded animate-pulse"></div>
                                        </td>

                                        <td className="p-4">
                                            <div className="h-8 w-24 bg-gray-200 rounded-full animate-pulse"></div>
                                        </td>

                                        <td className="p-4">
                                            <div className="h-10 w-24 bg-gray-200 rounded-lg animate-pulse"></div>
                                        </td>

                                    </tr>

                                ))

                            ) : leads.length > 0 ? (

                                leads.map((lead) => {

                                    const scoreColor =
                                        lead.commercial_score >= 70
                                            ? "bg-green-100 text-green-700"
                                            : lead.commercial_score >= 40
                                            ? "bg-orange-100 text-orange-700"
                                            : "bg-gray-100 text-gray-700";

                                    const statusColor = {
                                        New: "bg-blue-100 text-blue-700",
                                        Contacted: "bg-yellow-100 text-yellow-700",
                                        "Meeting Scheduled": "bg-purple-100 text-purple-700",
                                        "Proposal Sent": "bg-orange-100 text-orange-700",
                                        Won: "bg-green-100 text-green-700",
                                        Lost: "bg-red-100 text-red-700",
                                    };

                                    const priorityStyle = {
                                        HOT: "bg-red-100 text-red-700",
                                        WARM: "bg-orange-100 text-orange-700",
                                        MEDIUM: "bg-blue-100 text-blue-700",
                                        LOW: "bg-gray-100 text-gray-700",
                                    };

                                    const priorityIcon = {
                                        HOT: "🔥",
                                        WARM: "🟠",
                                        MEDIUM: "🔵",
                                        LOW: "⚪",
                                    };

                                    const platformIcon = {
                                        Reddit: "👽",
                                        "Hacker News": "💻",
                                        "Product Hunt": "🚀",
                                        "Dev.to": "📰",
                                        RSS: "📡",
                                    };

                                    const serviceIcon = {
                                        website: "🌐",
                                        frontend: "💻",
                                        backend: "⚙️",
                                        ecommerce: "🛒",
                                        automation: "🤖",
                                        "AI & Automation": "🤖",
                                        "Data Analytics": "📊",
                                        "API Integration": "🔗",
                                        custom_software: "🧩",
                                    };

                                    const scoreBadge = (score) => {

                                        if (score >= 80)
                                            return "bg-green-100 text-green-700";

                                        if (score >= 60)
                                            return "bg-yellow-100 text-yellow-700";

                                        if (score >= 40)
                                            return "bg-orange-100 text-orange-700";

                                        return "bg-red-100 text-red-700";

                                    };

                                    return (

                                        <tr
                                            key={lead.id}
                                            className="border-b hover:bg-blue-50 transition duration-200"
                                        >

                                            <td className="p-4">

                                                <span
                                                    className={`px-3 py-1 rounded-full font-bold ${scoreColor}`}
                                                >
                                                    <>
                                                        {lead.commercial_score ?? 0}
                                                        <span className="text-xs ml-1">/100</span>
                                                    </>
                                                </span>

                                            </td>

                                            <td className="p-4 text-center">
                                                <span
                                                    className={`px-3 py-1 rounded-full font-semibold ${scoreBadge(
                                                        lead.buyer_intent_score ?? 0
                                                    )}`}
                                                >
                                                    {lead.buyer_intent_score ?? 0}
                                                </span>
                                            </td>

                                            <td className="p-4 text-center">
                                                <span
                                                    className={`px-3 py-1 rounded-full font-semibold ${scoreBadge(
                                                        lead.business_fit_score ?? 0
                                                    )}`}
                                                >
                                                    {lead.business_fit_score ?? 0}
                                                </span>
                                            </td>

                                            <td className="p-4 text-center">
                                                <span
                                                    className={`px-3 py-1 rounded-full font-semibold ${scoreBadge(
                                                        lead.qualification_score ?? 0
                                                    )}`}
                                                >
                                                    {lead.qualification_score ?? 0}
                                                </span>
                                            </td>

                                            <td className="p-4">

                                                <span
                                                    className={`px-3 py-1 rounded-full text-sm font-semibold ${
                                                        priorityStyle[lead.commercial_priority] ||
                                                        "bg-gray-100 text-gray-700"
                                                    }`}
                                                >
                                                    {priorityIcon[lead.commercial_priority] || "⚪"}{" "}
                                                    {lead.commercial_priority || "LOW"}
                                                </span>

                                            </td>

                                            <td className="p-4 font-medium text-gray-800">
                                                {lead.title}
                                            </td>

                                            <td className="p-4">
                                                <span className="px-3 py-1 rounded-full bg-indigo-100 text-indigo-700 text-sm font-medium">
                                                    {(serviceIcon[lead.primary_service] || "📌")}{" "}
                                                    {lead.primary_service || "Unknown"}
                                                </span>
                                            </td>

                                            <td className="p-4">
                                                <span
                                                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                                                        lead.budget
                                                            ? "bg-emerald-100 text-emerald-700"
                                                            : "bg-gray-100 text-gray-600"
                                                    }`}
                                                >
                                                    {lead.budget || "Unknown"}
                                                </span>
                                            </td>

                                            <td className="p-4 text-center">

                                                <span
                                                    className={`px-3 py-1 rounded-full text-sm font-semibold ${
                                                        (lead.bid_count ?? 0) <= 10
                                                            ? "bg-green-100 text-green-700"
                                                            : (lead.bid_count ?? 0) <= 30
                                                            ? "bg-yellow-100 text-yellow-700"
                                                            : "bg-red-100 text-red-700"
                                                    }`}
                                                >
                                                    {lead.bid_count ?? 0}
                                                </span>

                                            </td>

                                            <td className="p-4 text-center">

                                                <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-sm">

                                                    {lead.project_type || "Unknown"}

                                                </span>

                                            </td>

                                            <td className="p-4 text-center">

                                                {lead.marketplace_urgent ? (

                                                    <span className="px-3 py-1 rounded-full bg-red-100 text-red-700 font-semibold">

                                                        🚨 Yes

                                                    </span>

                                                ) : (

                                                    <span className="px-3 py-1 rounded-full bg-gray-100 text-gray-600">

                                                        No

                                                    </span>

                                                )}

                                            </td>

                                            <td className="p-4">
                                                {(platformIcon[lead.platform] || "🌐")}{" "}
                                                {lead.platform}
                                            </td>

                                            <td className="p-4">

                                                <span
                                                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                                                        statusColor[lead.crm_status] ||
                                                        "bg-gray-100 text-gray-700"
                                                    }`}
                                                >
                                                    {lead.crm_status}
                                                </span>

                                            </td>

                                            <td className="p-4">
                                                <span
                                                    className={`px-3 py-1 rounded-full text-sm font-semibold ${
                                                        lead.opportunity_status === "OPEN"
                                                            ? "bg-green-100 text-green-700"
                                                            : lead.opportunity_status === "UNKNOWN"
                                                            ? "bg-gray-100 text-gray-700"
                                                            : lead.opportunity_status === "CLOSED"
                                                            ? "bg-red-100 text-red-700"
                                                            : lead.opportunity_status === "EXPIRED"
                                                            ? "bg-orange-100 text-orange-700"
                                                            : lead.opportunity_status === "REMOVED"
                                                            ? "bg-gray-200 text-gray-700"
                                                            : "bg-gray-100 text-gray-700"
                                                    }`}
                                                >
                                                    {lead.opportunity_status || "UNKNOWN"}
                                                </span>
                                            </td>

                                            <td className="p-4 text-sm text-gray-600 whitespace-nowrap">
                                                {lead.freshness_checked_at
                                                    ? new Date(lead.freshness_checked_at).toLocaleString()
                                                    : "—"}
                                            </td>

                                            <td className="p-4">

                                                <Link
                                                    to={`/lead/${lead.id}`}
                                                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition inline-block"
                                                >
                                                    👁 View
                                                </Link>

                                            </td>

                                        </tr>

                                    );

                                })

                            ) : (

                                <tr>

                                    <td
                                        colSpan="16"
                                        className="text-center py-12 text-gray-500"
                                    >
                                        No leads found.
                                    </td>

                                </tr>

                            )}

                        </tbody>

                    </table>

                </div>

            </div>

            {/* Pagination */}

            <div className="flex flex-col md:flex-row justify-between items-center mt-6 gap-4">

                <div className="text-gray-600 text-sm">

                    Showing

                    <span className="font-semibold mx-1">
                        {startLead}-{endLead}
                    </span>

                    of

                    <span className="font-semibold mx-1">
                        {total}
                    </span>

                    Leads

                </div>

                <div className="flex items-center gap-3">

                    <button
                        onClick={() => setPage((prev) => prev - 1)}
                        disabled={page === 1}
                        className="
                            px-4
                            py-2
                            rounded-lg
                            bg-gray-200
                            hover:bg-gray-300
                            disabled:opacity-50
                            transition
                        "
                    >
                        ← Previous
                    </button>

                    <span className="font-semibold">

                        Page {page} / {totalPages}

                    </span>

                    <button
                        onClick={() => setPage((prev) => prev + 1)}
                        disabled={page >= totalPages}
                        className="
                            px-4
                            py-2
                            rounded-lg
                            bg-blue-600
                            hover:bg-blue-700
                            text-white
                            disabled:opacity-50
                            transition
                        "
                    >
                        Next →
                    </button>

                </div>

            </div>

        </div>

    );

}

export default Leads;