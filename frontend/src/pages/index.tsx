import { Box, List, ListItem, Typography } from "@mui/joy";
import { ListItemText } from "@mui/material";
import * as React from "react";


export default function HomePage() {
  return (
    <Box sx={{ p: 1 }}>
      
      <Typography level="title-lg" gutterBottom component="h5">
        Welcome to the Text-to-SQL Demo!
      </Typography>
      <Typography variant="plain">
        Use natural language to ask questions, and watch as our AI translates
        your queries into SQL commands. Simply type your question about the data
        in plain English and click <strong>Submit</strong>.
      </Typography>

      <Typography variant="plain">This demo allows you to:</Typography>

      <Box>
        <ListItem>
          <ListItemText primary="• Ask questions naturally – no SQL knowledge required!" />
        </ListItem>
        <ListItem>
          <ListItemText primary="• Get instant results from structured data" />
        </ListItem>
        <ListItem>
          <ListItemText primary="• Experiment freely with your dataset" />
        </ListItem>
      </Box>

      <Typography variant="plain">
        Ready to get started? Navigate to the <strong>"Ask SQL"</strong> section
        and type your first question!
      </Typography>
    </Box>
  );
}
