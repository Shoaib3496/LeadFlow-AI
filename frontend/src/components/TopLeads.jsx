import { useNavigate } from "react-router-dom";

function TopLeads({ leads, error = false }) {
    const navigate = useNavigate();

    const statusColor = {
        New: "bg-blue-100 text-blue-700",
        Contacted: "bg-yellow-100 text-yellow-700",
        "Meeting Scheduled": "bg-purple-100 text-purple-700",
        "Proposal Sent": "bg-orange-100 text-orange-700",
        Won: "bg-green-100 text-green-700",
        Lost: "bg-red-100 text-red-700",
    };

    const priorityColor = {
        HOT: "bg-red-100 text-red-700 border-red-200",
        WARM: "bg-orange-100 text-orange-700 border-orange-200",
        MEDIUM: "bg-yellow-100 text-yellow-700 border-yellow-200",
        LOW: "bg-gray-100 text-gray-700 border-gray-200",
    };

    const scoreColor = (score) => {
        if (score >= 70) {
            return "bg-green-100 text-green-700";
        }

        if (score >= 40) {
            return "bg-yellow-100 text-yellow-700";
        }

        return "bg-gray-100 text-gray-700";
        
    };

    // ERROR STATE
    if (error) {
        return (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">

                <h2 className="text-2xl font-bold text-gray-900">
                    Top Commercial Opportunities
                </h2>

                <p className="text-sm text-gray-500 mt-1">
                    Highest-ranked actionable leads based on commercial intelligence
                </p>

                <div className="mt-6 border border-red-200 bg-red-50 rounded-xl p-6 text-center">

                    <p className="font-semibold text-red-700">
                        Unable to load top opportunities
                    </p>

                    <p className="text-sm text-red-600 mt-2">
                        The Top Leads service is temporarily unavailable.
                        Refresh the dashboard to try again.
                    </p>

                </div>

            </div>
        );
    }

    if (!leads || leads.length === 0) {
        return (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
                <h2 className="text-2xl font-bold mb-4">
                    Top Commercial Opportunities
                </h2>

                <div className="text-center py-8">
                    <p className="text-gray-500">
                        No actionable commercial opportunities are available.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">

            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                        Top Commercial Opportunities
                    </h2>

                    <p className="text-gray-500 text-sm mt-1">
                        Highest-ranked actionable leads based on commercial intelligence
                    </p>
                </div>

                <span className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-semibold">
                    Top {leads.length}
                </span>
            </div>

            <div className="space-y-5">

                {leads.map((lead, index) => (
                    <div
                        key={lead.id}
                        className="
                            border
                            border-gray-200
                            rounded-2xl
                            p-5
                            hover:border-blue-400
                            hover:shadow-lg
                            transition-all
                        "
                    >

                        <div className="flex flex-col xl:flex-row xl:justify-between gap-5">

                            <div className="flex-1 min-w-0">

                                <div className="flex flex-wrap items-center gap-3 mb-3">

                                    <span className="bg-gray-900 text-white px-3 py-1 rounded-full text-sm font-bold">
                                        #{index + 1}
                                    </span>

                                    <div className="flex flex-wrap items-center gap-2">

                                        <span
                                            className={`
                                                px-3
                                                py-1
                                                rounded-full
                                                border
                                                text-sm
                                                font-semibold
                                                ${
                                                    priorityColor[lead.commercial_priority] ||
                                                    "bg-gray-100 text-gray-700 border-gray-200"
                                                }
                                            `}
                                        >
                                            Priority: {lead.commercial_priority || "N/A"}
                                        </span>

                                        <span
                                            className="
                                                bg-gray-100
                                                text-gray-700
                                                px-3
                                                py-1
                                                rounded-full
                                                text-sm
                                                font-medium
                                            "
                                        >
                                            Platform: {lead.platform || "Unknown"}
                                        </span>

                                        <span
                                            className="
                                                bg-indigo-50
                                                text-indigo-700
                                                px-3
                                                py-1
                                                rounded-full
                                                text-sm
                                                font-medium
                                            "
                                        >
                                            Service: {lead.primary_service || "Unknown"}
                                        </span>

                                        <span
                                            className={`
                                                px-3
                                                py-1
                                                rounded-full
                                                text-sm
                                                font-medium
                                                ${
                                                    statusColor[lead.crm_status] ||
                                                    "bg-gray-100 text-gray-700"
                                                }
                                            `}
                                        >
                                            Status: {lead.crm_status || "Unknown"}
                                        </span>

                                    </div>

                                </div>

                                <h3 className="font-bold text-lg text-gray-900">
                                    {lead.title || "Untitled Lead"}
                                </h3>

                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">

                                    <div className="bg-gray-50 rounded-xl p-3">
                                        <p className="text-xs text-gray-500">
                                            Buyer Intent
                                        </p>

                                        <p className="font-bold text-gray-900 mt-1">
                                            {lead.buyer_intent_score ?? 0}/100
                                        </p>
                                    </div>

                                    <div className="bg-gray-50 rounded-xl p-3">
                                        <p className="text-xs text-gray-500">
                                            Business Fit
                                        </p>

                                        <p className="font-bold text-gray-900 mt-1">
                                            {lead.business_fit_score ?? 0}/100
                                        </p>
                                    </div>

                                    <div className="bg-gray-50 rounded-xl p-3">
                                        <p className="text-xs text-gray-500">
                                            Qualification
                                        </p>

                                        <p className="font-bold text-gray-900 mt-1">
                                            {lead.qualification_score ?? 0}/100
                                        </p>
                                    </div>

                                    <div className="bg-gray-50 rounded-xl p-3">
                                        <p className="text-xs text-gray-500">
                                            Bids
                                        </p>

                                        <p className="font-bold text-gray-900 mt-1">
                                            {lead.bid_count ?? "N/A"}
                                        </p>
                                    </div>

                                </div>

                                <div className="mt-4">

                                    <p className="text-xs uppercase tracking-wide font-semibold text-gray-500">
                                        Budget
                                    </p>

                                    <p className="font-semibold text-gray-800 mt-1">
                                        {lead.budget || "Not specified"}
                                    </p>

                                </div>

                                {lead.ranking_reason && (
                                    <div className="mt-4 bg-blue-50 border border-blue-100 rounded-xl p-3">

                                        <p className="text-xs font-semibold text-blue-700 mb-1">
                                            Why this lead ranks highly
                                        </p>

                                        <p className="text-sm text-gray-600">
                                            {lead.ranking_reason}
                                        </p>

                                    </div>
                                )}

                            </div>

                            <div className="xl:w-48 flex xl:flex-col items-center xl:items-stretch justify-between xl:justify-start gap-3">

                                <div
                                    className={`
                                        text-center
                                        px-4
                                        py-3
                                        rounded-xl
                                        font-bold
                                        ${scoreColor(
                                            lead.commercial_score ?? 0
                                        )}
                                    `}
                                >
                                    <p className="text-xs font-semibold">
                                        Commercial Score
                                    </p>

                                    <p className="text-2xl mt-1">
                                        {lead.commercial_score ?? 0}
                                    </p>
                                </div>

                                <button
                                    type="button"
                                    onClick={() =>
                                        navigate(`/lead/${lead.id}`)
                                    }
                                    className="
                                        bg-blue-600
                                        hover:bg-blue-700
                                        text-white
                                        px-4
                                        py-2
                                        rounded-xl
                                        transition
                                        font-medium
                                    "
                                >
                                    View Details
                                </button>

                                {lead.link ? (

                                    <a
                                        href={lead.link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        onClick={(e) => e.stopPropagation()}
                                        className="
                                            block
                                            text-center
                                            border
                                            border-gray-300
                                            hover:bg-gray-50
                                            px-4
                                            py-2
                                            rounded-xl
                                            font-semibold
                                            transition
                                        "
                                    >
                                        Source ↗
                                    </a>

                                ) : (

                                    <button
                                        disabled
                                        className="
                                            w-full
                                            border
                                            border-gray-200
                                            bg-gray-50
                                            text-gray-400
                                            px-4
                                            py-2
                                            rounded-xl
                                            font-semibold
                                            cursor-not-allowed
                                        "
                                    >
                                        Source unavailable
                                    </button>

                                )}

                            </div>

                        </div>

                    </div>
                ))}

            </div>

        </div>
    );
}

export default TopLeads;