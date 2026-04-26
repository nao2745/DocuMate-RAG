import React from "react";
import { Composition } from "remotion";
import { DocuMatePromo } from "./Composition";

export const Root: React.FC = () => {
  return (
    <Composition
      id="DocuMatePromo"
      component={DocuMatePromo}
      durationInFrames={2700}
      fps={30}
      width={1280}
      height={720}
    />
  );
};
