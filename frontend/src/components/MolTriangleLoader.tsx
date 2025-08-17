import * as React from "react";
import SvgIcon from "@mui/material/SvgIcon";
import { motion, useReducedMotion } from "framer-motion";

type Props = {
    width?: number;
    height?: number;
    speed?: number;
};

function MolTriangleLoader({ width = 78, height = 11, speed = 1 }: Props) {
    const CRIMSON = "#ED1B29";
    const SEA_PINK = "#ED969E";
    const PERSIAN_PLUM = "#721C24";

    const BASE_OPACITY = 0.12;
    const MIN_FILL = 0.18;

    const prefersReduced = useReducedMotion();

    const cycle = 4.2 / speed;
    const N = 4;
    const slot = 1 / N;
    const overlap = 0.5;

    function timings(i: number) {
        const s = Math.max(0, i * slot - overlap * slot);
        const e = Math.min(1, (i + 1) * slot + overlap * slot);
        const mid = s + 0.6 * (e - s);
        return { s, mid, e };
    }

    const FacetFill = ({
                           d,
                           tx,
                           ty,
                           fill,
                           index,
                       }: {
        d: string;
        tx: number;
        ty: number;
        fill: string;
        index: number;
    }) => {
        if (prefersReduced) {
            return (
                <g transform="translate(-87.634447,-526.64827)">
                    <g transform="matrix(2.733567,0,0,-2.733567,-15.545133,587.31651)">
                        <path d={d} transform={`translate(${tx},${ty})`} fill={fill} />
                    </g>
                </g>
            );
        }

        const t = timings(index);

        return (
            <g transform="translate(-87.634447,-526.64827)">
                <g transform="matrix(2.733567,0,0,-2.733567,-15.545133,587.31651)">
                    <motion.path
                        d={d}
                        transform={`translate(${tx},${ty})`}
                        fill={fill}
                        initial={{ opacity: MIN_FILL }}
                        animate={{ opacity: [MIN_FILL, 1, MIN_FILL] }}
                        transition={{
                            duration: cycle,
                            times: [t.s, t.mid, t.e],
                            ease: "easeInOut",
                            repeat: Infinity,
                            repeatType: "loop",
                        }}
                    />
                </g>
            </g>
        );
    };

    const artRef = React.useRef<SVGGElement | null>(null);
    const [box, setBox] = React.useState<{ x: number; y: number; width: number; height: number } | null>(null);

    React.useLayoutEffect(() => {
        if (!artRef.current) return;
        const b = artRef.current.getBBox();
        if (b.width > 0 && b.height > 0) {
            setBox(b);
        }
    }, []);

    const viewBox = box
        ? `0 0 ${box.width} ${box.height}`
        : `0 0 279.01683 37.039831`; // fallback
    const shift = box ? `translate(${-box.x},${-box.y})` : undefined;

    return (
        <SvgIcon
            component={motion.svg}
            viewBox={viewBox}
            preserveAspectRatio="xMidYMid meet"
            sx={{ width, height }}
            focusable="false"
            aria-hidden
        >
            <g ref={artRef} transform={shift}>
                <g transform="translate(-87.634447,-526.64827)" opacity={BASE_OPACITY}>
                    <g transform="matrix(2.733567,0,0,-2.733567,-15.545133,587.31651)">
                        <path
                            d="M 0,0 11.736,-6.776 0,-13.55 0,0 Z"
                            transform="translate(37.7454,22.1938)"
                            fill={SEA_PINK}
                        />
                        <path
                            d="M 0,0 8.596,1.353 -3.139,-5.421 0,0 Z"
                            transform="translate(40.8853,14.0648)"
                            fill={PERSIAN_PLUM}
                        />
                        <path
                            d="m 0,0 -3.138,8.129 0,-13.55 L 0,0 Z"
                            transform="translate(40.8835,14.0648)"
                            fill={CRIMSON}
                        />
                        <path
                            d="M 0,0 -11.735,6.775 -8.595,-1.353 0,0 Z"
                            transform="translate(49.4809,15.4174)"
                            fill={CRIMSON}
                        />
                    </g>
                </g>

                <FacetFill
                    d="M 0,0 11.736,-6.776 0,-13.55 0,0 Z"
                    tx={37.7454}
                    ty={22.1938}
                    fill={SEA_PINK}
                    index={0}
                />
                <FacetFill
                    d="M 0,0 8.596,1.353 -3.139,-5.421 0,0 Z"
                    tx={40.8853}
                    ty={14.0648}
                    fill={PERSIAN_PLUM}
                    index={1}
                />
                <FacetFill
                    d="m 0,0 -3.138,8.129 0,-13.55 L 0,0 Z"
                    tx={40.8835}
                    ty={14.0648}
                    fill={CRIMSON}
                    index={2}
                />
                <FacetFill
                    d="M 0,0 -11.735,6.775 -8.595,-1.353 0,0 Z"
                    tx={49.4809}
                    ty={15.4174}
                    fill={CRIMSON}
                    index={3}
                />
            </g>
        </SvgIcon>
    );
}

export default MolTriangleLoader;
