import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
});

let authToken = "";

export function setAuthToken(token) {
  authToken = token || "";
}

api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

export async function bootstrapAuth() {
  return api.post("/auth/bootstrap");
}

export async function login(payload) {
  return api.post("/auth/login", payload);
}

export async function getCurrentUser() {
  return api.get("/auth/me");
}

export async function seedData() {
  return api.post("/seed");
}

export async function getPatients() {
  return api.get("/patients");
}

export async function createPatient(payload) {
  return api.post("/patients", payload);
}

export async function getSpecialties() {
  return api.get("/specialties");
}

export async function getPractitioners() {
  return api.get("/practitioners");
}

export async function getAppointments() {
  return api.get("/appointments");
}

export async function holdAppointment(payload) {
  return api.post("/appointments/slot-hold", payload);
}

export async function confirmAppointment(appointmentId) {
  return api.post(`/appointments/${appointmentId}/confirm`);
}

export async function cancelAppointment(appointmentId) {
  return api.post(`/appointments/${appointmentId}/cancel`);
}

export async function rescheduleAppointment(appointmentId, payload) {
  return api.post(`/appointments/${appointmentId}/reschedule`, payload);
}

export async function updateAppointmentStatus(appointmentId, status) {
  return api.post(`/appointments/${appointmentId}/status`, { status });
}

export async function getPractitionerQueue(practitionerId) {
  return api.get(`/practitioners/${practitionerId}/queue`);
}

export async function dispatchReminders() {
  return api.post("/reminders/dispatch");
}

export async function acknowledgeReminder(token) {
  return api.post(`/reminders/ack/${token}`);
}
