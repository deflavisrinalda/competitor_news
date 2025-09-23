#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from competitor_flow.crews.competitor_crew.competitor_crew import CompetitorCrew
from crewai.flow import Flow, listen, start


class CompetitorState(BaseModel):
    competitor: str = ""
    report: str = ""


class CompetitorFlow(Flow[CompetitorState]):

    @start()
    def ask_competitor(self):
        """
        Asks the user the competitor they want to research.
        """
        competitor = input("Enter the competitor you want to research: ")
        self.state.competitor = competitor

    @listen(ask_competitor)
    def generate_competitor_report(self):
        print("Generating competitor report")
        result = (
            CompetitorCrew()
            .crew()
            .kickoff(inputs={"competitor": self.state.competitor})
        )

        print("Competitor report generated", result.raw)
        self.state.report = result.raw


def kickoff():
    competitor_flow = CompetitorFlow()
    competitor_flow.kickoff()


def plot():
    competitor_flow = CompetitorFlow()
    competitor_flow.plot()


if __name__ == "__main__":
    kickoff()
