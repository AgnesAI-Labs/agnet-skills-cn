#!/usr/bin/env node
import { createRequire } from "node:module";
import { parseArgs } from "node:util";
import { evaluateOverflowMeasurement } from "../runtime/lib/layout-validation.mjs";
import { fitResumeLayout } from "../runtime/lib/resume-layout.mjs";
import { openResumePage } from "../runtime/lib/resume-page.mjs";

const require = createRequire(new URL("../runtime/package.json", import.meta.url));

const { values } = parseArgs({
  options: { html: { type: "string" } },
});

if (!values.html) {
  console.error("Usage: measure_resume_layout.mjs --html <resume.html>");
  process.exit(1);
}

let browser;
try {
  const { chromium } = require("playwright");
  browser = await chromium.launch({ headless: true });
  const page = await openResumePage(browser, values.html);
  const layout = await fitResumeLayout(page);
  if (layout.status === "degraded") {
    console.log(JSON.stringify(layout));
  } else {
    const result = evaluateOverflowMeasurement(layout.measurement);
    console.log(JSON.stringify({
      ...result,
      status: layout.status === "fail" ? "fail" : result.status,
      message: layout.status === "fail" ? layout.message : result.message,
      layout,
    }));
    if (layout.status === "fail" || result.status === "fail") process.exitCode = 1;
  }
  if (layout.status === "degraded") process.exitCode = 2;
} catch (error) {
  console.log(JSON.stringify({
    status: "degraded",
    message: `Playwright 布局测量不可用：${error.message}。请安装 Playwright 与 Chromium 后重试。`,
  }));
  process.exitCode = 2;
} finally {
  await browser?.close();
}
