import { useEffect, useMemo, useState } from "react";
import dayjs from "dayjs";
import { BellRing, CalendarCheck2, ClipboardPlus, LockKeyhole, Stethoscope, UserRoundPlus, UsersRound } from "lucide-react";
import {
  bootstrapAuth,
  cancelAppointment,
  confirmAppointment,
  createPatient,
  dispatchReminders,
  getAppointments,
  getCurrentUser,
  getPatients,
  getPractitionerQueue,
  getPractitioners,
  getSpecialties,
  holdAppointment,
  login,
  rescheduleAppointment,
  setAuthToken,
  updateAppointmentStatus,
} from "./api/client";

const STATUS_OPTIONS = [
  "Pending",
  "In Waiting Room",
  "In Consultation",
  "Completed",
  "Cancelled",
  "No-Show",
];

function toIso(localDateTime) {
  return new Date(localDateTime).toISOString();
}

function App() {
  const [auth, setAuth] = useState(null);
  const [loginForm, setLoginForm] = useState({ username: "admin", password: "admin123" });

  const [patients, setPatients] = useState([]);
  const [specialties, setSpecialties] = useState([]);
  const [practitioners, setPractitioners] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [queue, setQueue] = useState([]);
  const [selectedPractitioner, setSelectedPractitioner] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  const [patientForm, setPatientForm] = useState({
    full_name: "",
    date_of_birth: "",
    biological_sex: "",
    phone_number: "",
    email: "",
    known_allergies: "",
    government_id: "",
  });

  const [bookingForm, setBookingForm] = useState({
    patient_id: "",
    practitioner_id: "",
    specialty_id: "",
    start_datetime: "",
    end_datetime: "",
    created_by: "reception",
  });

  const [holdId, setHoldId] = useState(null);

  const role = auth?.role;
  const isAdmin = role === "admin";
  const isReception = role === "receptionist";
  const isPractitioner = role === "practitioner";
  const isPatient = role === "patient";

  const canCreatePatient = isAdmin || isReception;
  const canBookAppointments = isAdmin || isReception || isPatient;
  const canConfirmAppointments = isAdmin || isReception || isPatient;
  const canChangeStatus = isAdmin || isReception || isPractitioner;
  const canDispatchReminders = isAdmin || isReception;
  const canViewQueue = isAdmin || isReception || isPractitioner;

  const metrics = useMemo(() => {
    const pending = appointments.filter((a) => a.status === "Pending").length;
    const waiting = appointments.filter((a) => a.status === "In Waiting Room").length;
    const consultation = appointments.filter((a) => a.status === "In Consultation").length;
    return { pending, waiting, consultation, total: appointments.length };
  }, [appointments]);

  const visiblePatients = useMemo(() => {
    if (isPatient && auth?.linked_patient_id) {
      return patients.filter((p) => p.id === auth.linked_patient_id);
    }
    return patients;
  }, [patients, isPatient, auth]);

  const visiblePractitioners = useMemo(() => {
    if (isPractitioner && auth?.linked_practitioner_id) {
      return practitioners.filter((p) => p.id === auth.linked_practitioner_id);
    }
    return practitioners;
  }, [practitioners, isPractitioner, auth]);

  async function loadAll() {
    const [patientsRes, specialtiesRes, practitionersRes, appointmentsRes] = await Promise.all([
      getPatients(),
      getSpecialties(),
      getPractitioners(),
      getAppointments(),
    ]);
    setPatients(patientsRes.data);
    setSpecialties(specialtiesRes.data);
    setPractitioners(practitionersRes.data);
    setAppointments(appointmentsRes.data);

    const queueId =
      isPractitioner && auth?.linked_practitioner_id
        ? auth.linked_practitioner_id
        : selectedPractitioner
          ? Number(selectedPractitioner)
          : null;

    if (queueId && canViewQueue) {
      const queueRes = await getPractitionerQueue(queueId);
      setQueue(queueRes.data);
    } else {
      setQueue([]);
    }
  }

  useEffect(() => {
    (async () => {
      try {
        await bootstrapAuth();
      } catch {
        // Ignore: bootstrap is idempotent and may already be initialized.
      }
    })();
  }, []);

  useEffect(() => {
    if (!auth) return;
    (async () => {
      try {
        setBusy(true);
        await loadAll();
      } catch (error) {
        setMessage(error?.response?.data?.detail || "Could not load data");
      } finally {
        setBusy(false);
      }
    })();
  }, [auth]);

  useEffect(() => {
    if (!auth || !canViewQueue) return;
    if (isPractitioner && auth?.linked_practitioner_id) {
      (async () => {
        const queueRes = await getPractitionerQueue(auth.linked_practitioner_id);
        setQueue(queueRes.data);
      })();
      return;
    }

    if (!selectedPractitioner) return;
    (async () => {
      const queueRes = await getPractitionerQueue(Number(selectedPractitioner));
      setQueue(queueRes.data);
    })();
  }, [selectedPractitioner, auth]);

  async function doLogin(e) {
    e.preventDefault();
    try {
      setBusy(true);
      const loginRes = await login(loginForm);
      setAuthToken(loginRes.data.access_token);
      const meRes = await getCurrentUser();
      setAuth({
        ...meRes.data,
        linked_patient_id: loginRes.data.linked_patient_id,
        linked_practitioner_id: loginRes.data.linked_practitioner_id,
      });
      setMessage(`Signed in as ${meRes.data.role}.`);
    } catch (error) {
      setMessage(error?.response?.data?.detail || "Login failed");
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    setAuthToken("");
    setAuth(null);
    setPatients([]);
    setSpecialties([]);
    setPractitioners([]);
    setAppointments([]);
    setQueue([]);
    setMessage("Signed out.");
  }

  async function submitPatient(e) {
    e.preventDefault();
    try {
      setBusy(true);
      await createPatient(patientForm);
      setMessage("Patient registered successfully.");
      setPatientForm({
        full_name: "",
        date_of_birth: "",
        biological_sex: "",
        phone_number: "",
        email: "",
        known_allergies: "",
        government_id: "",
      });
      await loadAll();
    } catch (error) {
      setMessage(error?.response?.data?.detail || "Could not register patient");
    } finally {
      setBusy(false);
    }
  }

  async function holdSlot(e) {
    e.preventDefault();
    try {
      setBusy(true);
      const payload = {
        ...bookingForm,
        patient_id: Number(bookingForm.patient_id),
        practitioner_id: Number(bookingForm.practitioner_id),
        specialty_id: Number(bookingForm.specialty_id),
        start_datetime: toIso(bookingForm.start_datetime),
        end_datetime: toIso(bookingForm.end_datetime),
      };
      const res = await holdAppointment(payload);
      setHoldId(res.data.id);
      setMessage(`Slot held for 5 minutes. Hold ID: ${res.data.id}`);
      await loadAll();
    } catch (error) {
      setMessage(error?.response?.data?.detail || "Could not hold slot");
    } finally {
      setBusy(false);
    }
  }

  async function confirmHeld() {
    if (!holdId) return;
    try {
      setBusy(true);
      await confirmAppointment(holdId);
      setMessage(`Appointment ${holdId} confirmed and notifications triggered.`);
      setHoldId(null);
      await loadAll();
    } catch (error) {
      setMessage(error?.response?.data?.detail || "Could not confirm appointment");
    } finally {
      setBusy(false);
    }
  }

  async function runReminderDispatch() {
    try {
      setBusy(true);
      const res = await dispatchReminders();
      setMessage(`Reminder dispatch completed. Sent ${res.data.sent} reminders.`);
    } catch (error) {
      setMessage(error?.response?.data?.detail || "Could not dispatch reminders");
    } finally {
      setBusy(false);
    }
  }

  async function quickStatus(id, statusValue) {
    try {
      await updateAppointmentStatus(id, statusValue);
      await loadAll();
    } catch (error) {
      setMessage(error?.response?.data?.detail || "Could not update status");
    }
  }

  async function quickCancel(id) {
    try {
      await cancelAppointment(id);
      await loadAll();
    } catch (error) {
      setMessage(error?.response?.data?.detail || "Could not cancel appointment");
    }
  }

  async function moveByOneHour(id, startIso, endIso) {
    try {
      const newStart = dayjs(startIso).add(1, "hour").toISOString();
      const newEnd = dayjs(endIso).add(1, "hour").toISOString();
      await rescheduleAppointment(id, { start_datetime: newStart, end_datetime: newEnd });
      await loadAll();
    } catch (error) {
      setMessage(error?.response?.data?.detail || "Could not reschedule appointment");
    }
  }

  if (!auth) {
    return (
      <div className="shell">
        <div className="glow glow-1" />
        <div className="glow glow-2" />
        <header className="hero">
          <p className="eyebrow">Secure Access</p>
          <h1>MedSched Authentication</h1>
          <p>Sign in with a role account to access the authorized clinical workflow.</p>
        </header>

        {message ? <p className="message">{message}</p> : null}

        <section className="panel auth-panel">
          <h2>
            <LockKeyhole size={18} /> Login
          </h2>
          <form onSubmit={doLogin} className="form-grid">
            <input
              placeholder="Username"
              value={loginForm.username}
              onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={loginForm.password}
              onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
              required
            />
            <button type="submit" disabled={busy}>Sign In</button>
          </form>
          <p className="hint">Demo users: admin/admin123, reception/reception123, doctor.maya/doctor123, alina.patient/patient123</p>
        </section>
      </div>
    );
  }

  return (
    <div className="shell">
      <div className="glow glow-1" />
      <div className="glow glow-2" />
      <header className="hero">
        <p className="eyebrow">Medical Appointment Management</p>
        <h1>MedSched Control Center</h1>
        <p>Role: <strong>{auth.role}</strong> | User: <strong>{auth.username}</strong></p>
        <button className="ghost" onClick={logout}>Sign Out</button>
      </header>

      <section className="metrics-grid">
        <article className="metric-card">
          <UsersRound size={20} />
          <h3>Total Appointments</h3>
          <strong>{metrics.total}</strong>
        </article>
        <article className="metric-card">
          <CalendarCheck2 size={20} />
          <h3>Pending</h3>
          <strong>{metrics.pending}</strong>
        </article>
        <article className="metric-card">
          <ClipboardPlus size={20} />
          <h3>Waiting Room</h3>
          <strong>{metrics.waiting}</strong>
        </article>
        <article className="metric-card">
          <Stethoscope size={20} />
          <h3>In Consultation</h3>
          <strong>{metrics.consultation}</strong>
        </article>
      </section>

      {message ? <p className="message">{message}</p> : null}

      <main className="workspace-grid">
        {canCreatePatient ? (
          <section className="panel">
            <h2>
              <UserRoundPlus size={18} /> Patient Onboarding
            </h2>
            <form onSubmit={submitPatient} className="form-grid">
              <input placeholder="Full legal name" value={patientForm.full_name} onChange={(e) => setPatientForm({ ...patientForm, full_name: e.target.value })} required />
              <input type="date" value={patientForm.date_of_birth} onChange={(e) => setPatientForm({ ...patientForm, date_of_birth: e.target.value })} required />
              <select value={patientForm.biological_sex} onChange={(e) => setPatientForm({ ...patientForm, biological_sex: e.target.value })} required>
                <option value="">Biological sex</option>
                <option>Female</option>
                <option>Male</option>
                <option>Other</option>
              </select>
              <input placeholder="Primary phone number" value={patientForm.phone_number} onChange={(e) => setPatientForm({ ...patientForm, phone_number: e.target.value })} required />
              <input type="email" placeholder="Email" value={patientForm.email} onChange={(e) => setPatientForm({ ...patientForm, email: e.target.value })} required />
              <input placeholder="Government ID" value={patientForm.government_id} onChange={(e) => setPatientForm({ ...patientForm, government_id: e.target.value })} required />
              <textarea placeholder="Known clinical allergies" value={patientForm.known_allergies} onChange={(e) => setPatientForm({ ...patientForm, known_allergies: e.target.value })} rows={3} />
              <button disabled={busy} type="submit">Register Patient</button>
            </form>
          </section>
        ) : null}

        {canBookAppointments ? (
          <section className="panel">
            <h2>
              <CalendarCheck2 size={18} /> Slot Booking + 5-Min Hold
            </h2>
            <form onSubmit={holdSlot} className="form-grid">
              <select
                value={bookingForm.patient_id}
                onChange={(e) => setBookingForm({ ...bookingForm, patient_id: e.target.value })}
                required
              >
                <option value="">Select patient</option>
                {visiblePatients.map((patient) => (
                  <option key={patient.id} value={patient.id}>{patient.full_name}</option>
                ))}
              </select>
              <select value={bookingForm.practitioner_id} onChange={(e) => setBookingForm({ ...bookingForm, practitioner_id: e.target.value })} required>
                <option value="">Select practitioner</option>
                {visiblePractitioners.map((practitioner) => (
                  <option key={practitioner.id} value={practitioner.id}>{practitioner.full_name}</option>
                ))}
              </select>
              <select value={bookingForm.specialty_id} onChange={(e) => setBookingForm({ ...bookingForm, specialty_id: e.target.value })} required>
                <option value="">Select specialty</option>
                {specialties.map((specialty) => (
                  <option key={specialty.id} value={specialty.id}>{specialty.name}</option>
                ))}
              </select>
              <input type="datetime-local" value={bookingForm.start_datetime} onChange={(e) => setBookingForm({ ...bookingForm, start_datetime: e.target.value })} required />
              <input type="datetime-local" value={bookingForm.end_datetime} onChange={(e) => setBookingForm({ ...bookingForm, end_datetime: e.target.value })} required />
              <button disabled={busy} type="submit">Hold Slot</button>
            </form>
            {canConfirmAppointments ? (
              <button className="secondary" disabled={!holdId || busy} onClick={confirmHeld}>Confirm Held Appointment</button>
            ) : null}
          </section>
        ) : null}

        {canDispatchReminders ? (
          <section className="panel">
            <h2>
              <BellRing size={18} /> Reminders
            </h2>
            <button onClick={runReminderDispatch} className="secondary" disabled={busy}>Dispatch 24h Reminders</button>
          </section>
        ) : null}

        <section className="panel full-span">
          <h2>Consultation Flow + Waiting Room</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Patient</th>
                  <th>Practitioner</th>
                  <th>Start</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {appointments.map((a) => {
                  const patient = patients.find((p) => p.id === a.patient_id);
                  const practitioner = practitioners.find((p) => p.id === a.practitioner_id);
                  return (
                    <tr key={a.id}>
                      <td>{a.id}</td>
                      <td>{patient?.full_name || a.patient_id}</td>
                      <td>{practitioner?.full_name || a.practitioner_id}</td>
                      <td>{dayjs(a.start_datetime).format("MMM D, YYYY HH:mm")}</td>
                      <td>
                        {canChangeStatus ? (
                          <select value={a.status} onChange={(e) => quickStatus(a.id, e.target.value)}>
                            {STATUS_OPTIONS.map((opt) => (
                              <option key={opt} value={opt}>{opt}</option>
                            ))}
                          </select>
                        ) : (
                          a.status
                        )}
                      </td>
                      <td className="actions">
                        {(isAdmin || isReception || isPatient) ? (
                          <>
                            <button onClick={() => moveByOneHour(a.id, a.start_datetime, a.end_datetime)} className="ghost">+1h</button>
                            <button onClick={() => quickCancel(a.id)} className="ghost danger">Cancel</button>
                          </>
                        ) : (
                          <span>-</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        {canViewQueue ? (
          <section className="panel full-span">
            <h2>Practitioner Workspace Overview</h2>
            {isPractitioner ? null : (
              <div className="inline-form">
                <select value={selectedPractitioner} onChange={(e) => setSelectedPractitioner(e.target.value)}>
                  <option value="">Choose practitioner queue</option>
                  {practitioners.map((p) => (
                    <option key={p.id} value={p.id}>{p.full_name}</option>
                  ))}
                </select>
              </div>
            )}
            <div className="queue-list">
              {queue.map((item) => (
                <article key={item.id} className="queue-card">
                  <h3>Appointment #{item.id}</h3>
                  <p>Status: {item.status}</p>
                  <p>Arrival: {item.check_in_at ? dayjs(item.check_in_at).format("HH:mm:ss") : "Not checked in"}</p>
                  <p>Slot: {dayjs(item.start_datetime).format("MMM D HH:mm")}</p>
                </article>
              ))}
              {queue.length === 0 ? <p>No active queue records.</p> : null}
            </div>
          </section>
        ) : null}
      </main>
    </div>
  );
}

export default App;
