import { Stack } from "@mui/material";
import { styled } from "@mui/material/styles";

const Centered = styled(Stack)({
  justifyContent: "center",
  alignItems: "center",
});


const FullSizeCentered = styled(Centered)({
  width: "100%",
  height: "100%",
});

interface ImageProps {
  $width?: string | number;
  $height?: string | number;
}

const Image = styled("img")<ImageProps>(({ $width, $height }) => ({
  width: $width || "90%",
  height: $height || "90%",
  margin: 16,
  cursor: "pointer",
  color: "white",
  fill: "white",
  objectFit: "contain",
  transition: "transform 0.4s ease, filter 0.4s ease",
  filter: "brightness(100%)",

  "&:hover": {
    transform: "scale(1.08)",
    filter: "brightness(120%) saturate(120%)",
  },
}));
export { Centered, FullSizeCentered, Image };
