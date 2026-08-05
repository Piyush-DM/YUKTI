import { Composition } from "remotion";
import { CANVAS } from "./system/tokens";
import { HARNESS_DURATION, SystemHarness } from "./harness/SystemHarness";
import { movementByIndex } from "./registry/movements";
import { BUILT_MOVEMENTS } from "./movements";
import { movementTiming } from "./movements/shared";
import { Master, MASTER_DURATION } from "./Master";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="Master"
      component={Master}
      durationInFrames={MASTER_DURATION}
      fps={CANVAS.fps}
      width={CANVAS.width}
      height={CANVAS.height}
    />

    {BUILT_MOVEMENTS.map(({ index, component }) => {
      const movement = movementByIndex(index);
      return (
        <Composition
          key={movement.numeral}
          id={`M${String(index).padStart(2, "0")}-${movement.name}`}
          component={component}
          durationInFrames={movementTiming(index).durationInFrames}
          fps={CANVAS.fps}
          width={CANVAS.width}
          height={CANVAS.height}
        />
      );
    })}

    <Composition
      id="SystemHarness"
      component={SystemHarness}
      durationInFrames={HARNESS_DURATION}
      fps={CANVAS.fps}
      width={CANVAS.width}
      height={CANVAS.height}
    />
  </>
);
