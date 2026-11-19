// gta6-meme-x-01 entry program (Node 22, standard library only).
//
// The entry itself is a post on X: a GTA 6 meme whose picture shows the
// make.fun ghost as Dr. Ghost, signing a launch-day sick note. This
// repository names that post in POST.json, and the house reads the post
// from X itself. All this program has to do is hand POST.json to the
// gate: copy it from the repository root (MAKEFUN_BOT_DIR) into the
// output directory (MAKEFUN_OUTPUT_DIR, /output on the grader).
//
// The copy is byte-for-byte and the program reads nothing else, so two
// runs always write the same bytes. Before copying, the file is parsed
// and checked to be a JSON object whose "url" names an X post, so a
// malformed POST.json fails loudly here instead of at the gate.
//
// Local run, the way the grader does it:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const botDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const source = join(botDir, "POST.json");
const target = join(outputDir, "POST.json");

let raw: string;
try {
  raw = readFileSync(source, "utf8");
} catch (err) {
  console.error(`cannot read ${source}: ${(err as Error).message}`);
  process.exit(1);
}

let post: unknown;
try {
  post = JSON.parse(raw);
} catch (err) {
  console.error(`POST.json is not valid JSON: ${(err as Error).message}`);
  process.exit(1);
}

const url = (post as { url?: unknown })?.url;
if (typeof url !== "string" || !url.startsWith("https://x.com/")) {
  console.error(`POST.json must name an X post: {"url": "https://x.com/<handle>/status/<id>"}`);
  process.exit(1);
}

mkdirSync(outputDir, { recursive: true });
writeFileSync(target, raw);
