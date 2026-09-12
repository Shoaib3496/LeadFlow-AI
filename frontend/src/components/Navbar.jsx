function Navbar() {

    const today = new Date().toLocaleDateString(undefined, {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
    });

    return (

        <header className="bg-white border-b border-gray-200 px-8 py-5 flex justify-between items-center shadow-sm">

            {/* Left */}

            <div>

                <h2 className="text-3xl font-bold text-gray-800">
                    Dashboard
                </h2>

                <p className="text-gray-500 mt-1">
                    {today}
                </p>

            </div>

            {/* Right */}

            <div className="flex items-center gap-6">

                {/* Status */}

                <div className="hidden md:flex items-center gap-2 bg-green-50 text-green-700 px-4 py-2 rounded-full">

                    <span className="w-2 h-2 rounded-full bg-green-500"></span>

                    <span className="text-sm font-medium">
                        System Online
                    </span>

                </div>

                {/* Notifications */}

                <button
                    className="
                        h-11
                        w-11
                        rounded-full
                        bg-gray-100
                        hover:bg-gray-200
                        transition
                        text-xl
                    "
                >
                    🔔
                </button>

                {/* Profile */}

                <div className="flex items-center gap-3">

                    <div
                        className="
                            h-11
                            w-11
                            rounded-full
                            bg-blue-600
                            text-white
                            flex
                            items-center
                            justify-center
                            font-bold
                            text-lg
                        "
                    >
                        MS
                    </div>

                    <div className="hidden md:block">

                        <p className="font-semibold text-gray-800">
                            Mohammad Shoaib
                        </p>

                        <p className="text-sm text-gray-500">
                            Administrator
                        </p>

                    </div>

                </div>

            </div>

        </header>

    );

}

export default Navbar;