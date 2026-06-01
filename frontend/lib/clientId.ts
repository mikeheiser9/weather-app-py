/**
 * Auth-free client identity. A single UUID is generated once and stored in
 * localStorage; it is sent as X-Client-Id on favorites and history requests so
 * those resources are scoped per browser without any login.
 */

const STORAGE_KEY = "wp-client-id";

function createUuid(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export function getClientId(): string {
  if (typeof window === "undefined") {
    return "";
  }
  let id = window.localStorage.getItem(STORAGE_KEY);
  if (!id) {
    id = createUuid();
    window.localStorage.setItem(STORAGE_KEY, id);
  }
  return id;
}
