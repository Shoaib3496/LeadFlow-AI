import { useEffect, useState } from "react";
import api from "../services/api";

function ScraperManager() {

    const [sources, setSources] = useState([]);

    const [loadingSources, setLoadingSources] = useState(false);

    const [pipelineState, setPipelineState] = useState("IDLE");

    const [pipelineResult, setPipelineResult] = useState({
        collected: 0,
        duplicates: 0,
        saved: 0
    });

    const [pipelineError, setPipelineError] = useState("");

    async function loadSources() {

        try {

            setLoadingSources(true);

            const response = await api.get("/sources");

            setSources(response.data);

        } catch (error) {

            console.error(
                "Failed to load sources:",
                error
            );

        } finally {

            setLoadingSources(false);

        }

    }

    useEffect(() => {

        loadSources();

        checkPipelineStatus();

    }, []);

    const enabledSources = sources.filter(
        source => source.enabled
    );

    async function checkPipelineStatus() {

        try {

            const response = await api.get(
                "/pipeline-status"
            );

            const data = response.data;

            setPipelineState(
                data.state || "IDLE"
            );

            if (data.result) {

                setPipelineResult({
                    collected: data.result.collected || 0,
                    duplicates: data.result.duplicates || 0,
                    saved: data.result.saved || 0
                });

            }

            if (data.error) {

                setPipelineError(data.error);

            }

            return data;

        } catch (error) {

            console.error(
                "Failed to get pipeline status:",
                error
            );

            return null;

        }

    }

    async function runScraper() {

        if (enabledSources.length === 0) {

            return;

        }

        setPipelineError("");

        setPipelineResult({
            collected: 0,
            duplicates: 0,
            saved: 0
        });

        try {

            const response = await api.post(
                "/run-production-pipeline"
            );

            console.log(
                "Production pipeline started:",
                response.data
            );

            setPipelineState("RUNNING");

            pollPipelineStatus();

        } catch (error) {

            console.error(
                "Failed to start production pipeline:",
                error
            );

            setPipelineState("FAILED");

            setPipelineError(
                error.response?.data?.message ||
                error.response?.data?.detail ||
                "Failed to start lead collection."
            );

        }

    }

    function pollPipelineStatus() {

        const interval = setInterval(
            async () => {

                const data =
                    await checkPipelineStatus();

                if (!data) {

                    return;

                }

                if (
                    data.state === "COMPLETED" ||
                    data.state === "FAILED"
                ) {

                    clearInterval(interval);

                }

            },
            2000
        );

    }

    function getStatusText() {

        if (pipelineState === "RUNNING") {
            return "Running";
        }

        if (pipelineState === "COMPLETED") {
            return "Completed";
        }

        if (pipelineState === "FAILED") {
            return "Failed";
        }

        return "Ready";

    }

    function getStatusClass() {

        if (pipelineState === "RUNNING") {

            return "bg-yellow-100 text-yellow-700";

        }

        if (pipelineState === "COMPLETED") {

            return "bg-green-100 text-green-700";

        }

        if (pipelineState === "FAILED") {

            return "bg-red-100 text-red-700";

        }

        return "bg-gray-100 text-gray-700";

    }

    return (

        <div className="max-w-7xl mx-auto space-y-8">

            <div>

                <h1 className="text-3xl font-bold text-gray-900">
                    Scraper Manager
                </h1>

                <p className="text-gray-500 mt-2">
                    Control lead collection and monitor the production pipeline.
                </p>

            </div>


            {/* Pipeline Status */}

            <div className="bg-white rounded-xl shadow p-6">

                <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">

                    <div>

                        <h2 className="text-xl font-semibold">
                            Pipeline Status
                        </h2>

                        <p className="text-gray-500 mt-1">
                            Current production lead collection status.
                        </p>

                    </div>

                    <span
                        className={`
                            px-4
                            py-2
                            rounded-full
                            font-semibold
                            ${getStatusClass()}
                        `}
                    >

                        {pipelineState === "RUNNING" && (
                            <span className="mr-2">
                                ●
                            </span>
                        )}

                        {getStatusText()}

                    </span>

                </div>

            </div>


            {/* Pipeline Statistics */}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                <div className="bg-white rounded-xl shadow p-6">

                    <p className="text-gray-500">
                        Number Collected
                    </p>

                    <h2 className="text-3xl font-bold text-blue-600 mt-2">

                        {pipelineResult.collected}

                    </h2>

                </div>


                <div className="bg-white rounded-xl shadow p-6">

                    <p className="text-gray-500">
                        Number Duplicates
                    </p>

                    <h2 className="text-3xl font-bold text-orange-500 mt-2">

                        {pipelineResult.duplicates}

                    </h2>

                </div>


                <div className="bg-white rounded-xl shadow p-6">

                    <p className="text-gray-500">
                        Number Saved
                    </p>

                    <h2 className="text-3xl font-bold text-green-600 mt-2">

                        {pipelineResult.saved}

                    </h2>

                </div>

            </div>


            {/* Error */}

            {pipelineState === "FAILED" && pipelineError && (

                <div className="bg-red-50 border border-red-200 rounded-xl p-4">

                    <p className="font-semibold text-red-700">
                        Pipeline Failed
                    </p>

                    <p className="text-red-600 mt-1">
                        {pipelineError}
                    </p>

                </div>

            )}


            {/* Enabled Sources */}

            <div className="bg-white rounded-xl shadow p-6">

                <h2 className="text-xl font-semibold mb-4">
                    Enabled Sources
                </h2>

                {loadingSources ? (

                    <p className="text-gray-500">
                        Loading sources...
                    </p>

                ) : enabledSources.length === 0 ? (

                    <p className="text-gray-500">
                        No enabled sources found.
                    </p>

                ) : (

                    <div className="space-y-3 mb-8">

                        {enabledSources.map((source) => (

                            <div
                                key={source.id}
                                className="
                                    flex
                                    justify-between
                                    items-center
                                    border
                                    rounded-lg
                                    p-3
                                "
                            >

                                <span className="font-medium">
                                    {source.name}
                                </span>

                                <span className="text-green-600 font-semibold">
                                    Enabled
                                </span>

                            </div>

                        ))}

                    </div>

                )}


                <button
                    onClick={runScraper}
                    disabled={
                        pipelineState === "RUNNING" ||
                        enabledSources.length === 0
                    }
                    className="
                        bg-blue-600
                        text-white
                        px-6
                        py-3
                        rounded-lg
                        hover:bg-blue-700
                        disabled:opacity-50
                        disabled:cursor-not-allowed
                    "
                >

                    {pipelineState === "RUNNING"
                        ? "Running..."
                        : "Start Lead Collection"}

                </button>

            </div>

        </div>

    );

}

export default ScraperManager;