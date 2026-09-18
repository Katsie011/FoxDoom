/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FOXGLOVE_WS?: string;
  readonly VITE_FOXGLOVE_ORG?: string;
  readonly VITE_FOXGLOVE_CONTROL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
