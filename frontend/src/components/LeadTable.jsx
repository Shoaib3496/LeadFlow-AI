import { Link } from "react-router-dom";


function LeadTable({ leads = [] }) {

    // =====================================================
    // PRIORITY BADGE
    // =====================================================

    function getPriorityStyle(priority) {

        switch (priority) {

            case "HOT":
                return "bg-red-100 text-red-700 border-red-200";

            case "WARM":
                return "bg-orange-100 text-orange-700 border-orange-200";

            case "MEDIUM":
                return "bg-blue-100 text-blue-700 border-blue-200";

            case "LOW":
                return "bg-gray-100 text-gray-700 border-gray-200";

            default:
                return "bg-gray-100 text-gray-600 border-gray-200";
        }
    }


    // =====================================================
    // CRM STATUS BADGE
    // =====================================================

    function getStatusStyle(status) {

        switch (status) {

            case "New":
                return "bg-blue-100 text-blue-700";

            case "Contacted":
                return "bg-yellow-100 text-yellow-700";

            case "Qualified":
                return "bg-purple-100 text-purple-700";

            case "Proposal":
                return "bg-orange-100 text-orange-700";

            case "Won":
                return "bg-green-100 text-green-700";

            case "Lost":
                return "bg-red-100 text-red-700";

            default:
                return "bg-gray-100 text-gray-700";
        }
    }


    // =====================================================
    // SCORE STYLE
    // =====================================================

    function getScoreStyle(score) {

        if (score >= 70) {
            return "text-green-600";
        }

        if (score >= 40) {
            return "text-orange-600";
        }

        return "text-gray-500";
    }


    // =====================================================
    // EMPTY STATE
    // =====================================================

    if (!leads.length) {

        return (

            <div className="py-14 text-center">

                <div className="text-4xl mb-3">
                    📭
                </div>

                <h3 className="text-lg font-semibold text-gray-800">
                    No recent leads
                </h3>

                <p className="text-sm text-gray-500 mt-2">
                    New leads will appear here after the pipeline collects them.
                </p>

            </div>

        );
    }


    return (

        <div>

            {/* ================================================= */}
            {/* HEADER */}
            {/* ================================================= */}

            <div className="flex items-center justify-between mb-6">

                <div>

                    <h2 className="text-xl font-bold text-gray-900">
                        Recent Leads
                    </h2>

                    <p className="text-sm text-gray-500 mt-1">
                        Latest opportunities collected by LeadFlow AI
                    </p>

                </div>


                <Link
                    to="/leads"
                    className="
                        text-sm
                        font-semibold
                        text-blue-600
                        hover:text-blue-800
                        transition
                    "
                >
                    View All Leads →
                </Link>

            </div>


            {/* ================================================= */}
            {/* TABLE */}
            {/* ================================================= */}

            <div className="overflow-x-auto">

                <table className="min-w-full">

                    <thead>

                        <tr className="border-b border-gray-200">

                            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase">
                                Lead
                            </th>

                            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase">
                                Source
                            </th>

                            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase">
                                Service
                            </th>

                            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase">
                                Score
                            </th>

                            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase">
                                Priority
                            </th>

                            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase">
                                CRM Status
                            </th>

                            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase">
                                Budget
                            </th>

                            <th className="text-right py-3 px-4 text-xs font-semibold text-gray-500 uppercase">
                                Action
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        {leads.map((lead) => (

                            <tr
                                key={lead.id}
                                className="
                                    border-b
                                    border-gray-100
                                    hover:bg-gray-50
                                    transition
                                "
                            >

                                {/* LEAD */}

                                <td className="py-4 px-4">

                                    <div className="max-w-xs">

                                        <p
                                            className="
                                                font-semibold
                                                text-gray-900
                                                truncate
                                            "
                                            title={lead.title}
                                        >
                                            {lead.title || "Untitled Lead"}
                                        </p>

                                        <p className="text-xs text-gray-400 mt-1">
                                            ID #{lead.id}
                                        </p>

                                    </div>

                                </td>


                                {/* SOURCE */}

                                <td className="py-4 px-4">

                                    <span
                                        className="
                                            inline-flex
                                            px-3
                                            py-1
                                            rounded-full
                                            text-xs
                                            font-medium
                                            bg-gray-100
                                            text-gray-700
                                        "
                                    >
                                        {lead.platform || "Unknown"}
                                    </span>

                                </td>


                                {/* SERVICE */}

                                <td className="py-4 px-4 text-sm text-gray-700">

                                    {lead.primary_service || "Unknown"}

                                </td>


                                {/* COMMERCIAL SCORE */}

                                <td className="py-4 px-4">

                                    <span
                                        className={`
                                            text-lg
                                            font-bold
                                            ${getScoreStyle(
                                                lead.commercial_score || 0
                                            )}
                                        `}
                                    >
                                        {lead.commercial_score ?? 0}
                                    </span>

                                    <span className="text-xs text-gray-400">
                                        /100
                                    </span>

                                </td>


                                {/* PRIORITY */}

                                <td className="py-4 px-4">

                                    <span
                                        className={`
                                            inline-flex
                                            px-3
                                            py-1
                                            rounded-full
                                            border
                                            text-xs
                                            font-bold
                                            ${getPriorityStyle(
                                                lead.commercial_priority
                                            )}
                                        `}
                                    >
                                        {lead.commercial_priority || "LOW"}
                                    </span>

                                </td>


                                {/* CRM STATUS */}

                                <td className="py-4 px-4">

                                    <span
                                        className={`
                                            inline-flex
                                            px-3
                                            py-1
                                            rounded-full
                                            text-xs
                                            font-semibold
                                            ${getStatusStyle(
                                                lead.crm_status
                                            )}
                                        `}
                                    >
                                        {lead.crm_status || "New"}
                                    </span>

                                </td>


                                {/* BUDGET */}

                                <td className="py-4 px-4">

                                    <p className="text-sm font-medium text-gray-700 whitespace-nowrap">

                                        {lead.budget || "Unknown"}

                                    </p>

                                </td>


                                {/* ACTION */}

                                <td className="py-4 px-4">

                                    <div className="flex items-center justify-end gap-2">

                                        {/* Internal Lead Details */}
                                        

                                        <Link
                                            to={`/lead/${lead.id}`}
                                            className="
                                                inline-flex
                                                items-center
                                                justify-center
                                                px-3
                                                py-2
                                                rounded-lg
                                                bg-blue-50
                                                text-blue-700
                                                text-sm
                                                font-semibold
                                                hover:bg-blue-100
                                                transition
                                                whitespace-nowrap
                                            "
                                        >
                                            View
                                        </Link>


                                        {/* Original Marketplace / Source */}

                                        {lead.link ? (

                                            <a
                                                href={lead.link}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="
                                                    inline-flex
                                                    items-center
                                                    justify-center
                                                    px-3
                                                    py-2
                                                    rounded-lg
                                                    bg-gray-100
                                                    text-gray-700
                                                    text-sm
                                                    font-semibold
                                                    hover:bg-gray-200
                                                    transition
                                                    whitespace-nowrap
                                                "
                                                title={`Open original lead on ${lead.platform || "source"}`}
                                            >
                                                Source ↗
                                            </a>

                                        ) : (

                                            <span
                                                className="
                                                    px-3
                                                    py-2
                                                    text-sm
                                                    text-gray-400
                                                    whitespace-nowrap
                                                "
                                            >
                                                No Link
                                            </span>

                                        )}

                                    </div>

                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

        </div>

    );

}


export default LeadTable;