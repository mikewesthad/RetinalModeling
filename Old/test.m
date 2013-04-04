% Modeled here as a sum of weights times there
% We need to model pieces of here


initialActivity = [10 0 0 0 0 0];

sd = 1;
w1 = exp(-[0 1 2 3 4 5]./sd);
w2 = exp(-[1 0 1 2 3 4]./sd);
w3 = exp(-[2 1 0 1 2 3]./sd);
w4 = exp(-[3 2 1 0 1 2]./sd);
w5 = exp(-[4 3 2 1 0 1]./sd);
w6 = exp(-[5 4 3 2 1 0]./sd);

w = [w1; w2; w3; w4; w5; w6];
w = w ./ sum(sum(w));
% % w = w .* 6;
% for i=1:6
%     w(i,:) = w(i,:) ./ sum(w(i,:));
% end



timesteps = 10000;
lastActivity = initialActivity;
figure();

maxy = max(max(w));
for i=1:6
    subplot(2,3,i), plot(w(i,:)), ylim([0,maxy])    
end

figure(2);
barGraph = bar(lastActivity);
ylim([0, 10]);

fps = 30;
for t=1:timesteps
    tic
   
    for i=1:6
        newActivity(i) = dot(lastActivity, w(i,:));
    end
    lastActivity = newActivity;
%     disp(max(newActivity)-min(newActivity));
    
    
    set(barGraph, 'Ydata', lastActivity);
    
    
    disp(sum(newActivity));
    
    timeElapsed = toc;
    if timeElapsed < 1/fps
        pause(1/fps - timeElapsed);
    else
        disp('Desired framerate unattainable');
    end    

end