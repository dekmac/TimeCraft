import React from 'react';
import type { GeneratedTag } from '../types/api';

interface TagsDisplayProps {
  tags: GeneratedTag[];
}

export const TagsDisplay: React.FC<TagsDisplayProps> = ({ tags }) => {
  if (tags.length === 0) {
    return null;
  }

  return (
    <div className="glass-effect p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Generated Tags</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tags.map((tag, index) => (
          <div key={index} className="p-4 bg-white/50 rounded-lg">
            <h4 className="font-medium text-gray-800">{tag.tag}</h4>
            <p className="text-sm text-gray-600 mt-1">{tag.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
