import { useState } from "react";
import { Check, ChevronLeft, X } from "lucide-react";
import "./profile.css";

interface ProfileProps {
  profileName: string;
  onSave: (name: string) => void;
  onBack: () => void;
}

export default function Profile({ profileName, onSave, onBack }: ProfileProps) {
  const [mode, setMode] = useState<"choice" | "create" | "login">("choice");
  const [email, setEmail] = useState(
    profileName.includes("@") ? profileName : "",
  );
  const [name, setName] = useState(
    profileName.includes("@") ? "" : profileName,
  );
  const [error, setError] = useState("");
  function save() {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setError("Введите адрес электронной почты");
      return;
    }
    onSave(name.trim() || email.trim());
  }

  return (
    <section className="profile-screen">
      <header className="screen-topbar">
        <button
          className="icon-button"
          aria-label={mode === "choice" ? "Назад" : "Отмена"}
          onClick={() => (mode === "choice" ? onBack() : setMode("choice"))}
        >
          {mode === "choice" ? <ChevronLeft /> : <X />}
        </button>
        <h1>
          {mode === "choice"
            ? "Профиль"
            : mode === "create"
              ? "Создать профиль"
              : "Вход в профиль"}
        </h1>
        {mode === "choice" ? (
          <span />
        ) : (
          <button
            className="icon-button"
            aria-label="Сохранить профиль"
            onClick={save}
          >
            <Check />
          </button>
        )}
      </header>
      {mode === "choice" ? (
        <div className="profile-choices">
          <button className="profile-create" onClick={() => setMode("create")}>
            СОЗДАТЬ ПРОФИЛЬ
          </button>
          <button className="profile-login" onClick={() => setMode("login")}>
            У МЕНЯ ЕСТЬ ПРОФИЛЬ
          </button>
        </div>
      ) : (
        <form
          className="profile-form"
          onSubmit={(event) => {
            event.preventDefault();
            save();
          }}
        >
          <label>
            Электронная почта
            <input
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
                setError("");
              }}
              placeholder="name@example.com"
              required
            />
          </label>
          <label>
            Имя
            <input
              value={name}
              autoComplete="name"
              onChange={(event) => setName(event.target.value)}
              placeholder="Как к вам обращаться"
              maxLength={70}
            />
          </label>
          <p className="profile-local-note">
            Демонстрационный профиль сохраняется в этом браузере.
          </p>
          {error && (
            <p className="profile-form-error" role="alert">
              {error}
            </p>
          )}
          <button type="submit" className="profile-save">
            {mode === "create" ? "Создать профиль" : "Продолжить"}
          </button>
        </form>
      )}
    </section>
  );
}
