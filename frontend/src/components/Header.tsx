import GitHubLogo from "./GitHubLogo";

export default function Header() {
  return (
    <header className="header" role="banner">
      <GitHubLogo className="header__logo" />
      <div className="header__text">
        <h1>GitHub Searcher</h1>
        <p>Search users or repositories below</p>
      </div>
    </header>
  );
}
