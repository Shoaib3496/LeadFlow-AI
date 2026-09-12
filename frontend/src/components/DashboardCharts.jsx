import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Legend,
    CartesianGrid
} from "recharts";


const PRIORITY_COLORS = {
    HOT: "#dc2626",
    WARM: "#f59e0b",
    MEDIUM: "#2563eb",
    LOW: "#6b7280"
};


const SERVICE_COLORS = [
    "#2563eb",
    "#16a34a",
    "#9333ea",
    "#dc2626",
    "#f59e0b",
    "#14b8a6",
    "#4f46e5",
    "#db2777"
];


function DashboardCharts({ analytics = {} }) {

    // =====================================================
    // SOURCE PERFORMANCE
    // =====================================================

    const sourceData = (
        analytics.source_performance || []
    ).map((source) => ({
        platform: source.platform || "Unknown",
        total: source.total || 0,
        actionable: source.actionable || 0,
        conversion_rate: source.conversion_rate || 0
    }));


    // =====================================================
    // PRIORITY DISTRIBUTION
    // =====================================================

    const priorityData = Object.entries(
        analytics.priority_distribution || {}
    ).map(([priority, count]) => ({
        priority,
        count
    }));


    // =====================================================
    // SERVICE DISTRIBUTION
    // =====================================================

    const serviceData = (
        analytics.service_distribution || []
    )
        .filter((item) => item.count > 0)
        .slice(0, 10)
        .map((item) => ({
            service: item.service || "Unknown",
            count: item.count || 0
        }));


    // =====================================================
    // EMPTY ANALYTICS CHECK
    // =====================================================

    const hasAnalytics =
        sourceData.length > 0 ||
        priorityData.length > 0 ||
        serviceData.length > 0;


    if (!hasAnalytics) {

        return (

            <div className="py-16 text-center">

                <div className="text-5xl mb-4">
                    📊
                </div>

                <h3 className="text-lg font-semibold text-gray-800">
                    No analytics available
                </h3>

                <p className="text-gray-500 mt-2">
                    Analytics will appear after leads are collected and processed.
                </p>

            </div>

        );

    }


    return (

        <div className="space-y-8">


            {/* ================================================= */}
            {/* ANALYTICS KPI STRIP */}
            {/* ================================================= */}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

                <div className="border border-gray-200 rounded-xl p-5">

                    <p className="text-sm text-gray-500">
                        Actionable Rate
                    </p>

                    <h3 className="text-3xl font-bold text-green-600 mt-2">
                        {analytics.actionable_rate ?? 0}%
                    </h3>

                    <p className="text-xs text-gray-400 mt-2">
                        Leads with commercial score ≥ 40
                    </p>

                </div>


                <div className="border border-gray-200 rounded-xl p-5">

                    <p className="text-sm text-gray-500">
                        Average Commercial Score
                    </p>

                    <h3 className="text-3xl font-bold text-blue-600 mt-2">
                        {analytics.average_commercial_score ?? 0}
                    </h3>

                    <p className="text-xs text-gray-400 mt-2">
                        Across all stored leads
                    </p>

                </div>


                <div className="border border-gray-200 rounded-xl p-5">

                    <p className="text-sm text-gray-500">
                        Best Commercial Score
                    </p>

                    <h3 className="text-3xl font-bold text-purple-600 mt-2">
                        {analytics.best_commercial_score ?? 0}
                    </h3>

                    <p className="text-xs text-gray-400 mt-2">
                        Highest-ranked opportunity
                    </p>

                </div>

            </div>


            {/* ================================================= */}
            {/* SOURCE PERFORMANCE */}
            {/* ================================================= */}

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">


                <div className="border border-gray-200 rounded-2xl p-6">

                    <div className="flex items-center justify-between mb-6">

                        <div>

                            <h2 className="text-xl font-bold text-gray-800">
                                🌐 Source Performance
                            </h2>

                            <p className="text-sm text-gray-500 mt-1">
                                Total vs actionable leads by source
                            </p>

                        </div>

                        <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-semibold">

                            {sourceData.length} Sources

                        </span>

                    </div>


                    {sourceData.length > 0 ? (

                        <ResponsiveContainer width="100%" height={340}>

                            <BarChart data={sourceData}>

                                <CartesianGrid
                                    strokeDasharray="3 3"
                                    stroke="#e5e7eb"
                                />

                                <XAxis
                                    dataKey="platform"
                                    tick={{ fontSize: 11 }}
                                    interval={0}
                                    angle={-20}
                                    textAnchor="end"
                                    height={75}
                                />

                                <YAxis />

                                <Tooltip />

                                <Legend />

                                <Bar
                                    dataKey="total"
                                    name="Total Leads"
                                    fill="#2563eb"
                                    radius={[6, 6, 0, 0]}
                                />

                                <Bar
                                    dataKey="actionable"
                                    name="Actionable"
                                    fill="#16a34a"
                                    radius={[6, 6, 0, 0]}
                                />

                            </BarChart>

                        </ResponsiveContainer>

                    ) : (

                        <p className="text-gray-500 text-center py-20">
                            No source performance data.
                        </p>

                    )}

                </div>


                {/* ================================================= */}
                {/* PRIORITY DISTRIBUTION */}
                {/* ================================================= */}


                <div className="border border-gray-200 rounded-2xl p-6">

                    <div className="mb-6">

                        <h2 className="text-xl font-bold text-gray-800">
                            🎯 Commercial Priority Mix
                        </h2>

                        <p className="text-sm text-gray-500 mt-1">
                            Distribution of AI-ranked lead priorities
                        </p>

                    </div>


                    {priorityData.length > 0 ? (

                        <ResponsiveContainer width="100%" height={340}>

                            <PieChart>

                                <Pie
                                    data={priorityData}
                                    dataKey="count"
                                    nameKey="priority"
                                    outerRadius={115}
                                    innerRadius={65}
                                    paddingAngle={3}
                                    label={({ name, value }) =>
                                        `${name}: ${value}`
                                    }
                                >

                                    {priorityData.map((entry) => (

                                        <Cell
                                            key={entry.priority}
                                            fill={
                                                PRIORITY_COLORS[
                                                    entry.priority
                                                ] || "#6b7280"
                                            }
                                        />

                                    ))}

                                </Pie>

                                <Tooltip />

                                <Legend />

                            </PieChart>

                        </ResponsiveContainer>

                    ) : (

                        <p className="text-gray-500 text-center py-20">
                            No priority distribution data.
                        </p>

                    )}

                </div>

            </div>


            {/* ================================================= */}
            {/* SERVICE DISTRIBUTION */}
            {/* ================================================= */}


            <div className="border border-gray-200 rounded-2xl p-6">

                <div className="mb-6">

                    <h2 className="text-xl font-bold text-gray-800">
                        🧩 Service Demand
                    </h2>

                    <p className="text-sm text-gray-500 mt-1">
                        Most common services requested across collected leads
                    </p>

                </div>


                {serviceData.length > 0 ? (

                    <ResponsiveContainer width="100%" height={380}>

                        <BarChart
                            data={serviceData}
                            layout="vertical"
                            margin={{
                                top: 5,
                                right: 30,
                                left: 80,
                                bottom: 5
                            }}
                        >

                            <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="#e5e7eb"
                            />

                            <XAxis type="number" />

                            <YAxis
                                type="category"
                                dataKey="service"
                                width={120}
                                tick={{ fontSize: 12 }}
                            />

                            <Tooltip />

                            <Bar
                                dataKey="count"
                                name="Leads"
                                radius={[0, 6, 6, 0]}
                            >

                                {serviceData.map((entry, index) => (

                                    <Cell
                                        key={`${entry.service}-${index}`}
                                        fill={
                                            SERVICE_COLORS[
                                                index %
                                                SERVICE_COLORS.length
                                            ]
                                        }
                                    />

                                ))}

                            </Bar>

                        </BarChart>

                    </ResponsiveContainer>

                ) : (

                    <p className="text-gray-500 text-center py-20">
                        No service distribution data.
                    </p>

                )}

            </div>

        </div>

    );

}


export default DashboardCharts;