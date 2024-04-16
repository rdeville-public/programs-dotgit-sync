// in ".releaserc.js" or "release.config.js"

const dateFormat = require("dateformat");
const fs = require("fs");
const path = require("path");

const gitmojis = require("gitmojis").gitmojis;

const TEMPLATE_DIR = "./.semantic-release/templates/";
const template = fs.readFileSync(
  path.join(TEMPLATE_DIR, "default-template.hbs")
);
const commitTemplate = fs.readFileSync(
  path.join(TEMPLATE_DIR, "commit-template.hbs")
);

const MAJOR = "major";
const MINOR = "minor";
const PATCH = "patch";
const RULES = {
  major: gitmojis
    .filter(({ semver }) => semver === MAJOR)
    .map(({ emoji }) => emoji),
  minor: gitmojis
    .filter(({ semver }) => semver === MINOR)
    .map(({ emoji }) => emoji),
  patch: gitmojis
    .filter(({ semver }) => semver === PATCH)
    .map(({ emoji }) => emoji),
  others: gitmojis
    .filter(({ semver }) => semver === null)
    .map(({ emoji }) => emoji)
    .filter((emoji) => emoji != "👷"),
};

module.exports = {
  branches: [
    "main",
    "next",
    {
      name: "beta",
      prerelease: true,
    },
    {
      name: "alpha",
      prerelease: true,
    },
  ],
  plugins: [
    [
      "semantic-release-gitmoji",
      {
        releaseRules: RULES,
        releaseNotes: {
          template,
          partials: { commitTemplate },
          helpers: {
            datetime: function (format = "UTC:yyyy-mm-dd") {
              return dateFormat(new Date(), format);
            },
            commitlist: function (commits, options) {
              let commitlist = {};
              let currRule = null;
              const rules = RULES;
              for (const iGitmoji in commits) {
                currRule = null;
                for (const iRule in rules) {
                  if (rules[iRule].includes(iGitmoji)) {
                    if (
                      !Object.prototype.hasOwnProperty.call(commitlist, iRule)
                    ) {
                      commitlist[iRule] = [];
                    }
                    currRule = iRule;
                    break;
                  }
                }
                if (currRule != null) {
                  for (
                    let idxCommit = 0;
                    idxCommit < commits[iGitmoji].length;
                    idxCommit++
                  ) {
                    commitlist[currRule].push(commits[iGitmoji][idxCommit]);
                  }
                }
                options.data.root["commits"] = commitlist;
              }
            },
          },
          issueResolution: {
            template: "{baseUrl}/{owner}/{repo}/issues/{ref}",
            baseUrl: "https://github.com",
          },
        },
      },
    ],
    [
      "@semantic-release/changelog",
      {
        changelogFile: "CHANGELOG.md",
        changelogTitle: "# CHANGELOG",
      },
    ],
    // [
    //   "@semantic-release/git",
    //   {
    //     assets: ["CHANGELOG.md", "package.json"],
    //     message:
    //       "🔖 Release ${nextRelease.version} [NO-CI]\n\n${nextRelease.notes}",
    //   },
    // ],
  ],
  tagFormat: "${version}",
};
