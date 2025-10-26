import React from 'react';
import { Skeleton, Box, Stack } from '@mui/material';

/**
 * Reusable loading skeleton components for consistent loading states
 */

export interface ConversationSkeletonProps {
  count?: number;
}

/**
 * Skeleton for conversation list items
 */
export const ConversationSkeleton: React.FC<ConversationSkeletonProps> = ({ count = 5 }) => {
  return (
    <Stack spacing={1}>
      {Array.from({ length: count }).map((_, index) => (
        <Box key={index} sx={{ p: 2 }}>
          <Skeleton variant="text" width="70%" height={24} />
          <Skeleton variant="text" width="90%" height={20} sx={{ mt: 0.5 }} />
          <Skeleton variant="text" width="40%" height={16} sx={{ mt: 0.5 }} />
        </Box>
      ))}
    </Stack>
  );
};

export interface MessageSkeletonProps {
  count?: number;
}

/**
 * Skeleton for message items in chat
 */
export const MessageSkeleton: React.FC<MessageSkeletonProps> = ({ count = 3 }) => {
  return (
    <Stack spacing={3} sx={{ p: 2 }}>
      {Array.from({ length: count }).map((_, index) => {
        const isUser = index % 2 === 0;
        return (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: isUser ? 'flex-end' : 'flex-start',
              gap: 1,
            }}
          >
            {!isUser && <Skeleton variant="circular" width={40} height={40} />}
            <Box sx={{ maxWidth: '70%' }}>
              <Skeleton variant="text" width={200} height={24} />
              <Skeleton variant="rectangular" width="100%" height={60} sx={{ mt: 0.5, borderRadius: 2 }} />
              <Skeleton variant="text" width={100} height={16} sx={{ mt: 0.5 }} />
            </Box>
            {isUser && <Skeleton variant="circular" width={40} height={40} />}
          </Box>
        );
      })}
    </Stack>
  );
};

export interface SearchResultSkeletonProps {
  count?: number;
}

/**
 * Skeleton for search results
 */
export const SearchResultSkeleton: React.FC<SearchResultSkeletonProps> = ({ count = 5 }) => {
  return (
    <Stack spacing={2} sx={{ p: 2 }}>
      {/* Group header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Skeleton variant="circular" width={24} height={24} />
        <Skeleton variant="text" width={120} height={24} />
      </Box>
      
      {/* Result items */}
      {Array.from({ length: count }).map((_, index) => (
        <Box key={index} sx={{ p: 1.5, pl: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <Skeleton variant="text" width="60%" height={20} />
            <Skeleton variant="circular" width={20} height={20} />
          </Box>
          <Skeleton variant="text" width="90%" height={16} />
          <Skeleton variant="text" width="30%" height={14} sx={{ mt: 0.5 }} />
        </Box>
      ))}
    </Stack>
  );
};

export interface SpaceSkeletonProps {
  count?: number;
}

/**
 * Skeleton for space selector dropdown
 */
export const SpaceSkeleton: React.FC<SpaceSkeletonProps> = ({ count = 3 }) => {
  return (
    <Stack spacing={1} sx={{ p: 1 }}>
      {Array.from({ length: count }).map((_, index) => (
        <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1.5, p: 1 }}>
          <Skeleton variant="circular" width={32} height={32} />
          <Box sx={{ flex: 1 }}>
            <Skeleton variant="text" width="60%" height={20} />
            <Skeleton variant="text" width="40%" height={16} />
          </Box>
        </Box>
      ))}
    </Stack>
  );
};

export interface GraphSkeletonProps {}

/**
 * Skeleton for knowledge graph loading
 */
export const GraphSkeleton: React.FC<GraphSkeletonProps> = () => {
  return (
    <Box
      sx={{
        width: '100%',
        height: 400,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.paper',
        borderRadius: 2,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Animated network visualization skeleton */}
      <Box sx={{ position: 'relative', width: '80%', height: '80%' }}>
        {/* Center node */}
        <Skeleton
          variant="circular"
          width={60}
          height={60}
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
          }}
        />
        
        {/* Surrounding nodes */}
        {[
          { top: '20%', left: '30%' },
          { top: '20%', left: '70%' },
          { top: '80%', left: '30%' },
          { top: '80%', left: '70%' },
          { top: '50%', left: '10%' },
          { top: '50%', left: '90%' },
        ].map((position, index) => (
          <Skeleton
            key={index}
            variant="circular"
            width={40}
            height={40}
            sx={{
              position: 'absolute',
              ...position,
              transform: 'translate(-50%, -50%)',
            }}
          />
        ))}
        
        {/* Connecting lines */}
        {[
          { top: '35%', left: '40%', width: '20%', height: 2 },
          { top: '35%', left: '60%', width: '20%', height: 2 },
          { top: '65%', left: '40%', width: '20%', height: 2 },
          { top: '65%', left: '60%', width: '20%', height: 2 },
        ].map((line, index) => (
          <Skeleton
            key={index}
            variant="rectangular"
            sx={{
              position: 'absolute',
              ...line,
            }}
          />
        ))}
      </Box>
    </Box>
  );
};

export interface CardSkeletonProps {
  lines?: number;
}

/**
 * Generic card skeleton for various content
 */
export const CardSkeleton: React.FC<CardSkeletonProps> = ({ lines = 3 }) => {
  return (
    <Box sx={{ p: 2 }}>
      <Skeleton variant="text" width="60%" height={28} sx={{ mb: 1 }} />
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          variant="text"
          width={index === lines - 1 ? '70%' : '100%'}
          height={20}
          sx={{ mt: 0.5 }}
        />
      ))}
    </Box>
  );
};
