import React from 'react';
import {
  SafeAreaView,
  StatusBar,
  Text,
  useColorScheme,
  View,
} from 'react-native';
import {Colors} from 'react-native/Libraries/NewAppScreen';

function App(): JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';

  const backgroundStyle = {
    backgroundColor: isDarkMode ? Colors.darker : Colors.lighter,
    flex: 1,
  };

  return (
    <SafeAreaView style={backgroundStyle}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={backgroundStyle.backgroundColor}
      />
      <View
        // eslint-disable-next-line react-native/no-inline-styles
        style={{
          flex: 1,
          justifyContent: 'center',
          alignItems: 'center',
          padding: 20,
        }}>
        <Text
          // eslint-disable-next-line react-native/no-inline-styles
          style={{
            fontSize: 24,
            color: isDarkMode ? Colors.lighter : Colors.darker,
            marginBottom: 10,
          }}>
          FitMotion
        </Text>
        <Text
          // eslint-disable-next-line react-native/no-inline-styles
          style={{
            fontSize: 16,
            color: isDarkMode ? Colors.lighter : Colors.darker,
            textAlign: 'center',
          }}>
          Seu assistente de treino inteligente
        </Text>
      </View>
    </SafeAreaView>
  );
}

export default App;
