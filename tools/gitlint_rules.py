# -*- coding: utf-8 -*-

from gitlint.rules import ConfigurationRule


class MarkdownCodeBlockConfigurationRule(ConfigurationRule):
    """
    This rule ignores markdown code blocks
    """

    name = "ignore-markdown-code-blocks"
    id = "UCR1"

    def apply(self, config, commit):
        body = commit.message.body
        commit.message.body = []
        ignoring = False
        for line in body:
            if line.startswith("```"):
                ignoring = not ignoring
            if ignoring:
                continue
            commit.message.body.append(line)
