function StatCard({
    title,
    value,
    color,
    icon,
    subtitle
}) {

    return (

        <div
            className="
                relative
                overflow-hidden
                bg-white
                rounded-2xl
                p-6
                border
                border-gray-200
                shadow-md
                hover:shadow-2xl
                hover:-translate-y-2
                transition-all
                duration-300
                group
            "
        >

            {/* Decorative Background */}

            <div
                className="
                    absolute
                    top-0
                    right-0
                    h-24
                    w-24
                    rounded-full
                    bg-blue-50
                    -translate-y-10
                    translate-x-10
                    group-hover:scale-125
                    transition
                    duration-500
                "
            ></div>

            <div className="relative flex justify-between items-start">

                <div>

                    <p className="uppercase tracking-wider text-xs font-semibold text-gray-500">

                        {title}

                    </p>

                    <h2 className={`text-4xl font-extrabold mt-3 ${color}`}>

                        {value}

                    </h2>

                    {subtitle && (

                        <p className="text-sm text-gray-400 mt-3">

                            {subtitle}

                        </p>

                    )}

                </div>

                <div
                    className="
                        h-16
                        w-16
                        rounded-2xl
                        bg-gradient-to-br
                        from-blue-50
                        to-blue-100
                        flex
                        items-center
                        justify-center
                        text-4xl
                        shadow-sm
                        group-hover:scale-110
                        transition
                        duration-300
                    "
                >

                    {icon}

                </div>

            </div>

        </div>

    );

}

export default StatCard;