import { render, screen } from '@testing-library/react';
import App from './App';

test('renders OCR Text Extractor heading', () => {
    render(<App />);
    const headingElement = screen.getByText(/OCR Text Extractor/i);
    expect(headingElement).toBeInTheDocument();
});
