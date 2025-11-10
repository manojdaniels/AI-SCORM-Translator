<<<<<<< HEAD
// Simple SCORM API mock to allow local playback without LMS errors
window.API = window.API_1484_11 = {
  LMSInitialize: () => "true",
  LMSFinish: () => "true",
  LMSSetValue: () => "true",
  LMSGetValue: () => "",
  LMSCommit: () => "true",
  LMSGetLastError: () => "0",
  LMSGetErrorString: () => "No error",
  LMSGetDiagnostic: () => "No diagnostic",
  GetValue: () => "",
  SetValue: () => "true",
  Commit: () => "true",
  Initialize: () => "true",
  Terminate: () => "true",
};
// Suppress unload permission policy warnings in local playback
try {
  window.onunload = null;
  window.beforeunload = null;
} catch (e) {
  console.warn("⚠ Suppressed unload permission policy warning.");
}

console.log("✅ LMS API mock loaded (local mode)");
=======
// Simple SCORM API mock to allow local playback without LMS errors
window.API = window.API_1484_11 = {
  LMSInitialize: () => "true",
  LMSFinish: () => "true",
  LMSSetValue: () => "true",
  LMSGetValue: () => "",
  LMSCommit: () => "true",
  LMSGetLastError: () => "0",
  LMSGetErrorString: () => "No error",
  LMSGetDiagnostic: () => "No diagnostic",
  GetValue: () => "",
  SetValue: () => "true",
  Commit: () => "true",
  Initialize: () => "true",
  Terminate: () => "true",
};
console.log("✅ LMS API mock loaded (local mode)");
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
