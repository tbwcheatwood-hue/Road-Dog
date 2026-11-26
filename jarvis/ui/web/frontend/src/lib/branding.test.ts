import { describe, expect, it } from "vitest";

import {
  COMPANION_FULL_NAME,
  COMPANION_NAME,
  OFFICIAL_REPO_LABEL,
  OFFICIAL_REPO_SLUG,
  OFFICIAL_REPO_URL,
  PRODUCT_NAME,
  SECONDARY_TAGLINE,
  TAGLINE,
} from "@/lib/branding";

describe("branding identity", () => {
  it("keeps the current Road Dog values", () => {
    expect(PRODUCT_NAME).toBe("Road Dog");
    expect(OFFICIAL_REPO_SLUG).toBe("tbwcheatwood-hue/Road-Dog");
    expect(OFFICIAL_REPO_URL).toBe("https://github.com/tbwcheatwood-hue/Road-Dog");
    expect(OFFICIAL_REPO_LABEL).toBe("github.com/tbwcheatwood-hue/Road-Dog");
    expect(COMPANION_NAME).toBe("Sam");
    expect(COMPANION_FULL_NAME).toBe("Samwise");
    expect(TAGLINE).toBe("Every road is better with a Road Dog.");
    expect(SECONDARY_TAGLINE).toBe("Your AI. Your crew. Your road.");
  });
});
