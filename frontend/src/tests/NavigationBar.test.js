import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import NavigationBar from '../components/NavigationBar';

describe('NavigationBar', () => {
  test('renders EventEase brand', () => {
    render(
      <BrowserRouter>
        <NavigationBar />
      </BrowserRouter>
    );
    const brandElement = screen.getByText(/EventEase/i);
    expect(brandElement).toBeInTheDocument();
  });

  test('renders navigation links', () => {
    render(
      <BrowserRouter>
        <NavigationBar />
      </BrowserRouter>
    );
    expect(screen.getByText(/Home/i)).toBeInTheDocument();
    expect(screen.getByText(/Events/i)).toBeInTheDocument();
  });
});
