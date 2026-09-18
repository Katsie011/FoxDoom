/**
 * @foxglove/embed 0.79.0 imports `@foxglove/common` from a private monorepo
 * workspace (`0.0.0`). The published tarball does not include that package.
 * This shim covers the only runtime import (`toError` in ParentFetchBridge).
 */
export function toError(value: unknown): Error {
  if (value instanceof Error) {
    return value;
  }
  return new Error(String(value));
}

export type EmbeddedViewer = string;
