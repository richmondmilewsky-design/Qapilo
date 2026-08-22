// @ts-nocheck
import { ScrollViewStyleReset } from "expo-router/html";
import type { PropsWithChildren } from "react";

export default function Root({ children }: PropsWithChildren) {
  return (
    <html lang="en" style={{ height: "100%" }}>
      <head>
        <meta charSet="utf-8" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, shrink-to-fit=no, viewport-fit=cover"
        />
        {/*
          Disable body scrolling on web to make ScrollView components work correctly.
          If you want to enable scrolling, remove `ScrollViewStyleReset` and
          set `overflow: auto` on the body style below.
        */}
        <ScrollViewStyleReset />
        <style
          dangerouslySetInnerHTML={{
            __html: `
              /* Dynamic viewport height so Safari's collapsing address bar
                 doesn't cut off the bottom. dvh where supported, with a
                 -webkit-fill-available fallback for older iOS Safari. */
              html, body {
                height: 100vh !important;
                height: -webkit-fill-available !important;
              }
              @supports (height: 100dvh) {
                html, body { height: 100dvh !important; }
              }
              @supports (padding: max(0px, env(safe-area-inset-bottom))) {
                [role="tablist"] {
                  box-sizing: border-box !important;
                  height: calc(52px + max(10px, env(safe-area-inset-bottom))) !important;
                  min-height: calc(52px + max(10px, env(safe-area-inset-bottom))) !important;
                  padding-bottom: max(10px, env(safe-area-inset-bottom)) !important;
                }
              }
              body > div:first-child, #root { position: fixed !important; top: 0; left: 0; right: 0; bottom: 0; }
              [role="tablist"] [role="tab"] * { overflow: visible !important; }
              [role="heading"], [role="heading"] * { overflow: visible !important; }
            `,
          }}
        />
      </head>
      <body
        style={{
          margin: 0,
          height: "100%",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {children}
      </body>
    </html>
  );
}
