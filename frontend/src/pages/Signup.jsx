import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { UserPlus, User, Mail, Lock } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Signup() {
  const navigate = useNavigate();
  const { signup } = useAuth();

  const [form, setForm] = useState({
    fullName: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function handleChange(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      await signup(
        form.fullName,
        form.email,
        form.password
      );

      navigate("/login");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to create your account."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-icon">
          <UserPlus size={24} />
        </div>

        <h1>Create your account</h1>

        <p className="auth-subtitle">
          Start building your personal knowledge base.
        </p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <label>
            Full name
            <div className="input-wrapper">
              <User size={18} />
              <input
                type="text"
                name="fullName"
                placeholder="Your name"
                value={form.fullName}
                onChange={handleChange}
                required
              />
            </div>
          </label>

          <label>
            Email
            <div className="input-wrapper">
              <Mail size={18} />
              <input
                type="email"
                name="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>
          </label>

          <label>
            Password
            <div className="input-wrapper">
              <Lock size={18} />
              <input
                type="password"
                name="password"
                placeholder="Create a password"
                value={form.password}
                onChange={handleChange}
                minLength={6}
                required
              />
            </div>
          </label>

          <button
            className="primary-button"
            type="submit"
            disabled={submitting}
          >
            {submitting ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{" "}
          <Link to="/login">Sign in</Link>
        </p>
      </section>
    </main>
  );
}