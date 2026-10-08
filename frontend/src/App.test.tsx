import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("App", () => {
  it("states the research-only security boundary", () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain("does not prove identity");
    expect(markup).toContain("does not replace passwords");
  });
});
