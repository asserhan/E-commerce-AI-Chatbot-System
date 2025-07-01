import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2, ShoppingBag, Phone } from 'lucide-react';
import { chatAPI} from './services/api';
import './index.css';

// Message Component
const Message = ({ message, isBot, isTyping = false, products = [] }) => {
  return (
    <div className={`flex gap-3 mb-4 ${isBot ? 'justify-start' : 'justify-end'}`}>
      {isBot && (
        <div className="flex-shrink-0 w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
          <Bot size={16} className="text-white" />
        </div>
      )}
      
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
        isBot 
          ? 'bg-gray-100 text-gray-800' 
          : 'bg-primary-500 text-white ml-auto'
      }`}>
        {isTyping ? (
          <div className="flex items-center gap-1">
            <Loader2 size={16} className="animate-spin" />
            <span className="text-sm">AI is typing...</span>
          </div>
        ) : (
          <>
            <p className="text-sm leading-relaxed">{message}</p>
            {products && products.length > 0 && (
              <div className="mt-3 space-y-2">
                {products.map((product, index) => (
                  <ProductCard key={index} product={product} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
      
      {!isBot && (
        <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
          <User size={16} className="text-white" />
        </div>
      )}
    </div>
  );
};

// Product Card Component
const ProductCard = ({ product }) => {
  return (
    <div className="bg-white rounded-lg border p-3 shadow-sm">
      <div className="flex gap-3">
        {product.image && (
          <img 
            src={product.image} 
            alt={product.name}
            className="w-16 h-16 object-cover rounded"
          />
        )}
        <div className="flex-1">
          <h4 className="font-medium text-gray-900 text-sm">{product.name}</h4>
          <p className="text-xs text-gray-600 mt-1">{product.description}</p>
          <div className="flex items-center justify-between mt-2">
            <span className="font-bold text-primary-600">${product.price}</span>
            <ShoppingBag size={14} className="text-gray-400" />
          </div>
        </div>
      </div>
    </div>
  );
};

// Customer Info Form Component
const CustomerInfoForm = ({ onSubmit, onCancel, isLoading }) => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    age: '',
    phone: '',
    email: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="bg-white rounded-lg border p-4 shadow-sm">
      <h3 className="font-medium text-gray-900 mb-3">Share Your Contact Info</h3>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="grid grid-cols-2 gap-2">
          <input
            type="text"
            name="firstName"
            placeholder="First Name"
            value={formData.firstName}
            onChange={handleChange}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
          <input
            type="text"
            name="lastName"
            placeholder="Last Name"
            value={formData.lastName}
            onChange={handleChange}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>
        <input
          type="number"
          name="age"
          placeholder="Age"
          value={formData.age}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          required
        />
        <input
          type="tel"
          name="phone"
          placeholder="Phone Number"
          value={formData.phone}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          required
        />
        <input
          type="email"
          name="email"
          placeholder="Email (optional)"
          value={formData.email}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        <div className="flex gap-2">
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 bg-primary-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-600 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Phone size={16} />}
            Submit
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

// Main App Component
function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi! I'm your AI shopping assistant. How can I help you find the perfect product today?",
      isBot: true,
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [showCustomerForm, setShowCustomerForm] = useState(false);
  const [isSubmittingInfo, setIsSubmittingInfo] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Generate session ID
  useEffect(() => {
    const newSessionId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      isBot: false,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(inputValue, sessionId);
      
      const botMessage = {
        id: Date.now() + 1,
        text: response.response || response.message || "I'm sorry, I didn't understand that. Could you please rephrase?",
        isBot: true,
        timestamp: new Date(),
        products: response.products || []
      };

      setMessages(prev => [...prev, botMessage]);

      // Check if we should show customer form
      if (response.collect_info || response.show_form) {
        setShowCustomerForm(true);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "I'm experiencing some technical difficulties. Please try again in a moment.",
        isBot: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCustomerInfoSubmit = async (customerData) => {
    setIsSubmittingInfo(true);
    try {
      await chatAPI.submitCustomerInfo({
        ...customerData,
        session_id: sessionId
      });
      
      setShowCustomerForm(false);
      const confirmMessage = {
        id: Date.now(),
        text: "Thank you for sharing your information! Our sales team will contact you soon with personalized recommendations.",
        isBot: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, confirmMessage]);
    } catch (error) {
      console.error('Error submitting customer info:', error);
      const errorMessage = {
        id: Date.now(),
        text: "Sorry, there was an issue saving your information. Please try again.",
        isBot: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSubmittingInfo(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
            <Bot size={20} className="text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-gray-900">AI Shopping Assistant</h1>
            <p className="text-sm text-gray-600">Online • Ready to help</p>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto">
          {messages.map((message) => (
            <Message
              key={message.id}
              message={message.text}
              isBot={message.isBot}
              products={message.products}
            />
          ))}
          
          {/* Typing indicator */}
          {isLoading && (
            <Message isBot={true} isTyping={true} />
          )}

          {/* Customer info form */}
          {showCustomerForm && (
            <div className="mb-4">
              <CustomerInfoForm
                onSubmit={handleCustomerInfoSubmit}
                onCancel={() => setShowCustomerForm(false)}
                isLoading={isSubmittingInfo}
              />
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t px-4 py-3">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask me about products, prices, or anything..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              className="px-6 py-3 bg-primary-500 text-white rounded-full hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isLoading ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <Send size={20} />
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
