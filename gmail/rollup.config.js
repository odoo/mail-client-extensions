import typescript from "@rollup/plugin-typescript";
import { nodeResolve } from "@rollup/plugin-node-resolve";

const extensions = [".ts"];

/**
 * Prevent tree-shaking the entry-point
 * by not shaking any module that isn't imported by anyone.
 * @returns side-effects or nothing
 */
function preventEntrypointShakingPlugin() {
    return {
        name: "no-treeshaking",
        resolveId(id, importer) {
            if (!importer) {
                return { id, moduleSideEffects: "no-treeshake" };
            }
            return null;
        },
    };
}

export default {
    input: "./src/main.ts",
    output: {
        dir: "./build",
        format: "esm",
        sourcemap: true,
    },
    plugins: [
        preventEntrypointShakingPlugin(),
        nodeResolve({
            extensions,
        }),
        typescript(),
    ],
};
