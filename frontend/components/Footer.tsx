export function Footer(): React.ReactElement {
  return (
    <footer className="flex flex-col gap-1 border-t border-[var(--color-border)] pt-4 text-[0.7rem] text-[var(--color-text-faint)]">
      <span>
        Weather data by{" "}
        <a
          href="https://open-meteo.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[var(--color-text-dim)] underline decoration-dotted underline-offset-2"
        >
          Open-Meteo
        </a>{" "}
        under{" "}
        <a
          href="https://creativecommons.org/licenses/by/4.0/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[var(--color-text-dim)] underline decoration-dotted underline-offset-2"
        >
          CC BY 4.0
        </a>
        .
      </span>
    </footer>
  );
}
