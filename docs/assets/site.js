(() => {
  const pathParts = window.location.pathname.split("/").filter(Boolean);
  // Project Pages: https://user.github.io/radar_everything/
  const repoGuess = pathParts[0] || "radar_everything";
  const userGuess = window.location.hostname.replace(/\.github\.io$/i, "") || "YOUR_GITHUB_USER";
  const isGitHubPages = /\.github\.io$/i.test(window.location.hostname);
  const repoUrl = isGitHubPages
    ? `https://github.com/${userGuess}/${repoGuess}`
    : `https://github.com/${userGuess}/radar_everything`;

  const ids = ["repo-link", "repo-link-secondary", "readme-link", "manual-link", "listing-link"];
  const hrefMap = {
    "repo-link": repoUrl,
    "repo-link-secondary": repoUrl,
    "readme-link": `${repoUrl}#readme`,
    "manual-link": `${repoUrl}/blob/main/docs/MANUAL.md`,
    "listing-link": `${repoUrl}/blob/main/docs/GITHUB_LISTING.md`,
  };

  for (const id of ids) {
    const el = document.getElementById(id);
    if (el && hrefMap[id]) el.setAttribute("href", hrefMap[id]);
  }

  const note = document.getElementById("pages-note");
  if (note && isGitHubPages) {
    note.textContent = `GitHub Pages · ${userGuess}.github.io/${repoGuess}`;
  }

  const btn = document.querySelector(".copy-btn");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    const target = document.querySelector(btn.getAttribute("data-copy-target") || "");
    if (!target) return;
    const text = target.textContent
      .replace(/<your-account>/g, isGitHubPages ? userGuess : "<your-account>")
      .replace(/&lt;your-account&gt;/g, isGitHubPages ? userGuess : "<your-account>")
      .trim();
    try {
      await navigator.clipboard.writeText(text);
      const prev = btn.textContent;
      btn.textContent = "Copied";
      setTimeout(() => {
        btn.textContent = prev || "Copy commands";
      }, 1400);
    } catch {
      btn.textContent = "Copy failed";
    }
  });
})();
