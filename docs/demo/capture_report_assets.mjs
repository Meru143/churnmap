import path from "node:path";
import { pathToFileURL } from "node:url";

import { chromium } from "playwright";

const root = process.cwd();
const reportPath = path.resolve(root, "docs/demo/sample-report.html");
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({
  viewport: { width: 1360, height: 820 },
  deviceScaleFactor: 1,
});

await page.goto(pathToFileURL(reportPath).href, { waitUntil: "networkidle" });
await page.waitForSelector("rect.cell");
await page.screenshot({ path: "docs/assets/report-preview.png", fullPage: false });

await page.click('[data-tab="force"]');
await page.waitForTimeout(1200);
await page.screenshot({ path: "docs/assets/force-graph-preview.png", fullPage: false });

await browser.close();
