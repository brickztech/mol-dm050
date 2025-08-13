
  "use client";
  import { createTheme } from '@mui/material/styles';

  const theme = createTheme({
    cssVariables: {
      colorSchemeSelector: 'data-toolpad-color-scheme',
    },
    colorSchemes: {
      light: {
        palette: {
          mode: 'light',
          primary: {
            main: '#F1F1F1',
            dark: '#2f2a42',

          },
          secondary: {
            main: '#623BD1',
            light: '#F1F1F1',

          },
          background: {
            default: '#B19DE8',
            paper: '#675a8a',

          },
          text: {
            primary: 'rgb(255,255,255)',
            secondary: 'rgba(255,255,255,0.89)',


          },
            action: {
                active: '#F1F1F1',
                hover: 'rgba(196,251,128,0.48)',
              selected: '#c4fb80af',
              selectedOpacity: 1,
                hoverOpacity: 0.08,
                disabled: 'rgba(78,78,78,0.45)',
                disabledBackground: '#b5b5b5',
                disabledOpacity: 0.38,
                focusOpacity: 0.12,
                activatedOpacity: 0.24,
                pressedOpacity: 0.12,


            },
        },
      },
      dark: {
        palette: {
          mode: 'dark',
          primary: {
            main: '#90caf9',
          },
          secondary: {
            main: '#ce93d8',
          },
          background: {
            default: '#121212',
            paper: '#1e1e1e',
          },
          text: {
            primary: '#ffffff',
            secondary: '#cccccc',
          },
        },
      },
    },

  });

export default theme;
